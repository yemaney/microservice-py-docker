"""This module defines a router for vector search functionality."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlmodel import Session, select

from api.core import database, embeddings, models, oauth2

router = APIRouter(prefix="/search", tags=["Search"])


@router.get(
    "/files",
    response_model=list[models.FileSearchResult],
    status_code=status.HTTP_200_OK,
)
async def search_files(
    query: str = Query(..., description="Search query text"),
    limit: int = Query(10, description="Maximum number of results to return", ge=1, le=100),
    current_user: models.User = Depends(oauth2.get_current_user),
    session: Session = Depends(database.get_session),
):
    """
    Search for files using vector similarity based on text content.

    This endpoint generates an embedding for the search query and finds
    the most similar files in the user's collection using cosine similarity.

    Parameters
    ----------
    query : str
        The search query text to find similar files.
    limit : int, optional
        Maximum number of results to return (default: 10, max: 100).
    current_user : models.User
        The authenticated user performing the search.
    session : Session
        Database session.

    Returns
    -------
    List[models.FileSearchResult]
        List of search results with similarity scores.

    Raises
    ------
    HTTPException
        If there are issues with embedding generation or database queries.

    """
    try:
        # Generate embedding for the search query using OpenRouter API
        query_embedding = await embeddings.generate_embedding(query)

        # Perform vector similarity search using pgvector
        # Using cosine similarity (<=> operator in pgvector)
        stmt = text("""
            SELECT id, filename, content_type, size, user_id, created_at,
                   1 - (embedding <=> :query_embedding) as similarity
            FROM filemetadata
            WHERE user_id = :user_id
            ORDER BY embedding <=> :query_embedding
            LIMIT :limit
        """)

        results = session.execute(
            stmt,
            {
                "query_embedding": str(query_embedding),
                "user_id": current_user.id,
                "limit": limit,
            },
        ).fetchall()

        # Convert to response model using list comprehension
        return [
            models.FileSearchResult(
                id=row[0],
                filename=row[1],
                content_type=row[2],
                size=row[3],
                user_id=row[4],
                created_at=row[5],
                similarity=float(row[6]),
            )
            for row in results
        ]

    except HTTPException:
        raise
    except ValueError as e:
        msg = f"Error performing vector search: {e!s}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=msg,
        ) from e


@router.get(
    "/files/similar/{file_id}",
    response_model=list[models.FileSearchResult],
    status_code=status.HTTP_200_OK,
)
async def find_similar_files(
    file_id: int,
    limit: int = Query(10, description="Maximum number of results to return", ge=1, le=100),
    current_user: models.User = Depends(oauth2.get_current_user),
    session: Session = Depends(database.get_session),
):
    """
    Find files similar to an existing file in the user's collection.

    Parameters
    ----------
    file_id : int
        The ID of the file to find similar files for.
    limit : int, optional
        Maximum number of results to return (default: 10, max: 100).
    current_user : models.User
        The authenticated user.
    session : Session
        Database session.

    Returns
    -------
    List[models.FileSearchResult]
        List of similar files with similarity scores.

    Raises
    ------
    HTTPException
        If the file doesn't exist or belongs to another user.

    """
    # First, get the target file's embedding
    target_file = session.exec(
        select(models.FileMetadata).where(
            models.FileMetadata.id == file_id,
            models.FileMetadata.user_id == current_user.id,
        ),
    ).first()

    if not target_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or access denied",
        )

    try:
        # Find similar files using the target file's embedding
        stmt = text("""
            SELECT id, filename, content_type, size, user_id, created_at,
                   1 - (embedding <=> :target_embedding) as similarity
            FROM filemetadata
            WHERE user_id = :user_id AND id != :file_id
            ORDER BY embedding <=> :target_embedding
            LIMIT :limit
        """)

        results = session.execute(
            stmt,
            {
                "target_embedding": str(
                    target_file.embedding.tolist()
                    if hasattr(target_file.embedding, "tolist")
                    else target_file.embedding,
                ),
                "user_id": current_user.id,
                "file_id": file_id,
                "limit": limit,
            },
        ).fetchall()

        # Convert to response model using list comprehension
        return [
            models.FileSearchResult(
                id=row[0],
                filename=row[1],
                content_type=row[2],
                size=row[3],
                user_id=row[4],
                created_at=row[5],
                similarity=float(row[6]),
            )
            for row in results
        ]

    except HTTPException:
        raise
    except ValueError as e:
        msg = f"Error finding similar files: {e!s}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=msg,
        ) from e
