"""Tags resource mixin for PaperlessClient."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from easypaperless.models._base import MatchingAlgorithm
from easypaperless.models.permissions import SetPermissions
from easypaperless.models.tags import Tag

if TYPE_CHECKING:
    from easypaperless._internal.http import HttpSession
    from easypaperless._internal.resolvers import NameResolver


class TagsMixin:
    if TYPE_CHECKING:
        _session: HttpSession
        _resolver: NameResolver

        async def _list_resource(
            self, resource: str, model_class: type[Any], params: dict[str, Any] | None = None
        ) -> list[Any]: ...

        async def _get_resource(
            self, resource: str, id: int, model_class: type[Any]
        ) -> Any: ...

        async def _create_resource(
            self,
            resource: str,
            model_class: type[Any],
            *,
            owner: int | None = None,
            set_permissions: SetPermissions | None = None,
            **kwargs: Any,
        ) -> Any: ...

        async def _update_resource(
            self, resource: str, id: int, model_class: type[Any], **kwargs: Any
        ) -> Any: ...

        async def _delete_resource(self, resource: str, id: int) -> None: ...

    async def list_tags(
        self,
        *,
        ids: list[int] | None = None,
        name_contains: str | None = None,
        name_exact: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        ordering: str | None = None,
        descending: bool = False,
    ) -> list[Tag]:
        """Return tags defined in paperless-ngx.

        Args:
            ids: Return only tags whose ID is in this list.
            name_contains: Case-insensitive substring filter on tag name
                (raw API ``name__icontains``).
            name_exact: Case-insensitive exact match on tag name
                (raw API ``name__iexact``).
            page: Return only this specific page (1-based). Disables
                auto-pagination. Default: ``None`` (return all).
            page_size: Number of results per page. When omitted, the server
                default is used.
            ordering: Field to sort by. Examples: ``"name"``, ``"id"``.
            descending: When ``True``, reverses the sort direction of
                ``ordering``. Ignored when ``ordering`` is ``None``.

        Returns:
            List of :class:`~easypaperless.models.tags.Tag` objects.
        """
        params: dict[str, Any] = {}
        if ids is not None:
            params["id__in"] = ",".join(str(i) for i in ids)
        if name_contains is not None:
            params["name__icontains"] = name_contains
        if name_exact is not None:
            params["name__iexact"] = name_exact
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        if ordering is not None:
            params["ordering"] = f"-{ordering}" if descending else ordering
        return cast(list[Tag], await self._list_resource("tags", Tag, params or None))

    async def get_tag(self, id: int) -> Tag:
        """Fetch a single tag by its ID.

        Args:
            id: Numeric tag ID.

        Returns:
            The :class:`~easypaperless.models.tags.Tag` with the given ID.

        Raises:
            ~easypaperless.exceptions.NotFoundError: If no tag exists with
                that ID.
        """
        return cast(Tag, await self._get_resource("tags", id, Tag))

    async def create_tag(
        self,
        *,
        name: str,
        color: str | None = None,
        is_inbox_tag: bool | None = None,
        match: str | None = None,
        matching_algorithm: MatchingAlgorithm | None = None,
        is_insensitive: bool | None = None,
        parent: int | None = None,
        owner: int | None = None,
        set_permissions: SetPermissions | None = None,
    ) -> Tag:
        """Create a new tag.

        Args:
            name: Tag name. Must be unique.
            color: Background colour in the paperless-ngx UI as a CSS hex
                string (e.g. ``"#ff0000"``).
            is_inbox_tag: When ``True``, newly ingested documents receive this
                tag automatically until processed. At most one tag should be
                the inbox tag.
            match: Auto-matching pattern tested against incoming document
                content. Interpretation depends on ``matching_algorithm``.
            matching_algorithm: Controls how ``match`` is applied.
                See :class:`~easypaperless.models.MatchingAlgorithm`.
            is_insensitive: When ``True``, ``match`` is evaluated
                case-insensitively.
            parent: ID of an existing tag to use as parent, enabling
                hierarchical tag trees. ``None`` creates a root-level tag.
            owner: Numeric user ID to assign as owner. ``None`` creates the
                tag with no owner (visible to all users).
            set_permissions: Explicit view/change permission sets. Defaults to
                no permissions (all users have access via public visibility).

        Returns:
            The newly created :class:`~easypaperless.models.tags.Tag`.
        """
        return cast(Tag, await self._create_resource(
            "tags",
            Tag,
            owner=owner,
            set_permissions=set_permissions,
            name=name,
            color=color,
            is_inbox_tag=is_inbox_tag,
            match=match,
            matching_algorithm=matching_algorithm,
            is_insensitive=is_insensitive,
            parent=parent,
        ))

    async def update_tag(
        self,
        id: int,
        *,
        name: str | None = None,
        color: str | None = None,
        is_inbox_tag: bool | None = None,
        match: str | None = None,
        matching_algorithm: MatchingAlgorithm | None = None,
        is_insensitive: bool | None = None,
        parent: int | None = None,
    ) -> Tag:
        """Partially update a tag (PATCH semantics).

        Args:
            id: Numeric ID of the tag to update.
            name: Tag name. Must be unique.
            color: Background colour in the paperless-ngx UI as a CSS hex
                string (e.g. ``"#00ff00"``).
            is_inbox_tag: When ``True``, newly ingested documents receive this
                tag automatically until processed. At most one tag should be
                the inbox tag.
            match: Auto-matching pattern tested against incoming document
                content. Interpretation depends on ``matching_algorithm``.
            matching_algorithm: Controls how ``match`` is applied.
                See :class:`~easypaperless.models.MatchingAlgorithm`.
            is_insensitive: When ``True``, ``match`` is evaluated
                case-insensitively.
            parent: ID of an existing tag to use as parent, enabling
                hierarchical tag trees.

        Returns:
            The updated :class:`~easypaperless.models.tags.Tag`.
        """
        return cast(Tag, await self._update_resource(
            "tags",
            id,
            Tag,
            name=name,
            color=color,
            is_inbox_tag=is_inbox_tag,
            match=match,
            matching_algorithm=matching_algorithm,
            is_insensitive=is_insensitive,
            parent=parent,
        ))

    async def delete_tag(self, id: int) -> None:
        """Delete a tag.

        Args:
            id: Numeric ID of the tag to delete.

        Raises:
            ~easypaperless.exceptions.NotFoundError: If no tag exists with
                that ID.
        """
        await self._delete_resource("tags", id)
