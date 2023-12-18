from dataclasses import dataclass
from typing import Any

import ruamel.yaml
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.error import CommentMark
from ruamel.yaml.tokens import CommentToken

"""
TODO:
- [ ] Idea: DRY for `_get_map_comments` and `_get_seq_comments`.
- [ ] Idea: DRY for `map_sort_before` and `seq_sort_before`.
"""


def _comment_tokens_to_str(
    comment_tokens: None | CommentToken | list[CommentToken],
) -> str | None:
    """Convert CommentToken or list of CommentToken into string.

    Args:
        comments (Any): source for comments.

    Returns:
        str | None: string with joined comments.
    """
    if comment_tokens is None:
        return None

    if isinstance(comment_tokens, CommentToken):
        comment_tokens = [comment_tokens]

    tokens = []
    for token in comment_tokens:
        if token is None:
            continue
        elif isinstance(token, list):
            tokens.extend(token)
        else:
            tokens.append(token)

    comments: list[str] = []
    for token in tokens:
        if not token:
            continue
        assert token.value
        comments.append(token.value)

    return "".join(comments)


def _merge_comment_tokens(tokens: list[CommentToken]) -> CommentToken:
    assert len(tokens) > 0

    if len(tokens) == 1:
        return tokens[0]

    return _copy_comment_token(
        token=tokens[0],
        value=_comment_tokens_to_str(tokens),
    )


@dataclass
class Comments:
    """Helper class for comments.

    It provides possibility to handle comments in the same way
    for map and sequence items. It doesn't depend whether it
    CommentToke or list of CommentToken.
    """

    before: list[CommentToken] | None = None
    inline: list[CommentToken] | None = None
    after: list[CommentToken] | None = None


def _copy_comment_token(
    token: CommentToken,
    **kwargs,
) -> CommentToken:
    return CommentToken(
        value=kwargs["value"] if "value" in kwargs else token.value,
        start_mark=kwargs["start_mark"] if "start_mark" in kwargs else token.start_mark,
        end_mark=kwargs["end_mark"] if "end_mark" in kwargs else token.end_mark,
        column=kwargs["column"] if "column" in kwargs else token.column,
    )


def _get_comment_list(
    comment_tokens: None | CommentToken | list[CommentToken],
) -> None | list[CommentToken]:
    """Helper function to get list of CommentToken or None."""
    if comment_tokens is None:
        return None

    if isinstance(comment_tokens, CommentToken):
        comment_tokens = [comment_tokens]

    return comment_tokens


def _get_start_comments(
    comment_tokens: list[CommentToken] | None,
) -> Comments:
    """Get beginning comment (`.ca.comment`)."""

    res = Comments()
    if comment_tokens is None:
        return res

    assert len(comment_tokens) == 2
    assert comment_tokens[0] is None or isinstance(comment_tokens[0], CommentToken)
    assert comment_tokens[1] is None or isinstance(comment_tokens[1], list)

    res.before = _get_comment_list(comment_tokens[0])
    res.inline = _get_comment_list(comment_tokens[1])
    return res


def _get_map_comments(
    comment_tokens: list[CommentToken] | None,
) -> Comments:
    """Get comments for map items.

    Comment for current element is splitted into two: current element and after it.
    """

    res = Comments()
    if comment_tokens is None:
        return res

    assert len(comment_tokens) == 4
    assert comment_tokens[0] is None
    assert comment_tokens[2] is None or type(comment_tokens[2]) == CommentToken
    assert comment_tokens[3] is None or isinstance(comment_tokens[3], list)

    # "before" for map is in the [1]
    res.before = _get_comment_list(comment_tokens[1])

    # "inline" for map is in the [2]
    s = _comment_tokens_to_str(comment_tokens[2])
    if s is not None:
        if "\n" not in s:
            # no need to split "inline" comment
            res.inline = _get_comment_list(comment_tokens[2])
            return res

        # first line - inline comment
        # second line and others - for next elements
        current_after: list[str | None] = s.split("\n", 1)
        # replace with None if second line is empty
        if len(current_after) > 1 and current_after[1] == "":
            current_after[1] = None

        if current_after[0]:
            res.inline = [
                _copy_comment_token(
                    token=comment_tokens[2],
                    value=current_after[0],
                )
            ]
        if current_after[1]:
            # start_mark and columns have new indent
            res.after = [
                CommentToken(
                    value=current_after[1],
                    start_mark=CommentMark(0),
                    end_mark=comment_tokens[2].end_mark,
                    column=0,
                )
            ]

    if comment_tokens[3]:
        if res.after is None:
            res.after = []
        res.after.extend(_get_comment_list(comment_tokens[3]))

    return res


def map_sort_before(obj: CommentedMap, sorted_keys: list[Any]) -> CommentedMap:
    """Sort map with comments before a block.

    Args:
        obj (CommentedMap): source object
        sorted_keys (list[Any]): list of keys for resulting map

    Returns:
        CommentedMap: target object
    """
    assert isinstance(obj, CommentedMap)

    all_comments: dict[Any, Comments] = {}

    # Gather comments

    # First comment is handled specially
    comments = _get_start_comments(obj.ca.comment)
    assert comments.after is None
    prev_after = comments.inline
    # Next lines' comments
    for key in obj.keys():
        comments = _get_map_comments(obj.ca.items.get(key))

        # add "after" comment from previous element, if any
        if prev_after:
            if not comments.before:
                comments.before = []
            comments.before = prev_after + comments.before
            prev_after = None

        if not any(
            [isinstance(obj.get(key), cls) for cls in [CommentedMap, CommentedSeq]]
        ):
            # consider "after" comment as "before" only
            # for simple elements
            prev_after = comments.after
            comments.after = None
        all_comments[key] = comments

    if sorted_keys and (prev_after or obj.ca.end):
        last_key = sorted_keys[-1]
        inline = all_comments[last_key].inline
        # Combine inline and after comments
        if inline:
            inline[-1].value += "\n"
            inline += prev_after or []
            inline += _get_comment_list(obj.ca.end) or []
        else:
            inline = prev_after or []
            inline += _get_comment_list(obj.ca.end) or []
            inline[0].value = "\n" + inline[0].value
        all_comments[last_key].inline = inline

    # Create another map and put comments
    obj_sorted = CommentedMap()
    if obj.ca.comment and obj.ca.comment[0] is not None:
        obj_sorted.ca.comment = [obj.ca.comment[0], None]
        # obj_sorted.ca.comment = [
        #     CommentToken(
        #         value=obj.ca.comment[0],
        #         start_mark=CommentMark(0),  # reset line
        #     ),
        #     None,
        # ]
    for key in sorted_keys:
        obj_sorted[key] = obj[key]
        comments = all_comments[key]
        if comments.before:
            c = obj_sorted.ca.items.setdefault(key, [None, [], None, None])
            if c[1] is None:
                c[1] = []
            c[1].extend(comments.before)
        if comments.inline:
            assert type(comments.inline) == list
            c = obj_sorted.ca.items.setdefault(key, [None, None, None, None])
            assert c[2] is None
            c[2] = _merge_comment_tokens(comments.inline)
        if comments.after:
            c = obj_sorted.ca.items.setdefault(key, [None, None, None, []])
            if c[3] is None:
                c[3] = []
            c[3].extend(comments.after)

    return obj_sorted


def sorted_index(iterable, /, *, key=None, reverse=False) -> list[int]:
    """Wrapper for `sorted` function to return indices.

    Mainly uses for `seq_sort_before()` to generate `sorted_indices`.
    """

    # source values  [1, 5, 3, 2]
    # source index   [0, 1, 2, 3]
    # result values  [1, 2, 3, 5]
    # result indices [0, 3, 2, 1] <-- this is result
    return [
        i[0]
        for i in sorted(
            enumerate(iterable),
            key=lambda x: key(x[1]) if key is not None else x[1],
            reverse=reverse,
        )
    ]


def _get_seq_comments(
    comment_tokens: list[CommentToken] | None,
) -> Comments:
    """Get comments for seq items.

    Comment for current element is splitted into two: current element and after it.
    """

    res = Comments()
    if comment_tokens is None:
        return res

    assert len(comment_tokens) == 4
    assert comment_tokens[0] is not None
    assert comment_tokens[1] is None
    assert comment_tokens[2] is None
    assert comment_tokens[3] is None

    s = _comment_tokens_to_str(comment_tokens[0])
    # If no inline comment for current element
    if s is None:
        return res
    if "\n" not in s:
        # no need to split "inline" comment
        res.inline = _get_comment_list(comment_tokens[2])
        return res

    # first line - inline comment
    # second line and others - for next elements
    current_after: list[str | None] = s.split("\n", 1)
    # replace with None if second line is empty
    if len(current_after) > 1 and current_after[1] == "":
        current_after[1] = None

    assert type(comment_tokens[0]) == CommentToken
    if current_after[0]:
        res.inline = [
            _copy_comment_token(
                token=comment_tokens[0],
                value=current_after[0],
            )
        ]
    if current_after[1]:
        # start_mark and columns have new indent
        res.after = [
            CommentToken(
                value=current_after[1],
                start_mark=CommentMark(0),
                end_mark=comment_tokens[0].end_mark,
                column=0,
            )
        ]

    return res


def seq_sort_before(obj: CommentedSeq, sorted_indices: list[Any]) -> CommentedSeq:
    """Sort sequence with comments before a block.

    Args:
        obj (CommentedSeq): source object
        sorted_keys (list[Any]): list of indices for resulting list

    Returns:
        CommentedSeq: target object
    """
    assert isinstance(obj, CommentedSeq)

    all_comments: dict[int, Comments] = {}

    # Gather comments

    # First comment is handled specially
    comments = _get_start_comments(obj.ca.comment)
    assert comments.after is None
    prev_after = comments.inline
    # Next lines' comments
    for obj_index in range(len(obj)):
        comments = _get_seq_comments(obj.ca.items.get(obj_index))

        # add "after" comment from previous element, if any
        if prev_after:
            if not comments.before:
                comments.before = []
            comments.before = prev_after + comments.before

        prev_after = comments.after
        comments.after = None
        all_comments[obj_index] = comments

    if sorted_indices and (prev_after or obj.ca.end):
        last_key = sorted_indices[-1]
        inline = all_comments[last_key].inline
        # Combine inline and after comments
        if inline:
            inline[-1].value += "\n"
            inline += prev_after or []
            inline += _get_comment_list(obj.ca.end) or []
        else:
            inline = prev_after or []
            inline += _get_comment_list(obj.ca.end) or []
            inline[0].value = "\n" + inline[0].value
        all_comments[last_key].inline = inline

    # Create another list and put comments
    obj_sorted = CommentedSeq()
    for sorted_index, obj_index in enumerate(sorted_indices):
        obj_sorted.append(obj[obj_index])
        comments = all_comments[obj_index]
        if comments.before:
            c = obj_sorted.ca.items.setdefault(sorted_index, [None, [], None, None])
            if c[1] is None:
                c[1] = []
            c[1].extend(comments.before)
        if comments.inline:
            assert type(comments.inline) == list
            c = obj_sorted.ca.items.setdefault(sorted_index, [None, None, None, None])
            assert c[0] is None
            c[0] = _merge_comment_tokens(comments.inline)
        assert comments.after is None

    return obj_sorted
