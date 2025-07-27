from fastapi import FastAPI, Path, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()

class Book:
    def __init__(self, id, title, author, description, rating, publish_date) -> None:
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.publish_date = publish_date
    
    def dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "description": self.description,
            "rating": self.rating,
            "publish_date": self.publish_date
        }

class BookRequest(BaseModel):
    id: Optional[int] = Field(description="Not required when creating new book", default=None)
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1)
    rating: int = Field(gt=0, lt=6)
    publish_date: int = Field(gt=1000, lt=9999)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Book Title",
                "author": "Book author",
                "description": "Book description",
                "rating": 5,
                "publish_date": 2026
            }
        }
    }

BOOKS = [
    Book(1, "Computer Science Book", "Luis", "book about computer science", 4, 2001),
    Book(2, "Math Book", "Aaron", "book about cars", 5, 2002),
    Book(3, "Computer Science Book", "Mia", "book about makeup", 4, 2003),
    Book(4, "Computer Science Book", "Adelyza", "book about unicorns", 2, 2004),
    Book(5, "Computer Science Book", "Aelanie", "book about minions", 2, 2005)
]

def set_book_id(book: Book) -> Book:
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book

@app.get("/books", status_code=status.HTTP_200_OK)
def read_all_books():
    return [book.dict() for book in BOOKS]

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
def get_book_by_id(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book.dict()
    raise HTTPException(status_code=404, detail="Book not found.")

@app.get("/books/rating/filter", status_code=status.HTTP_200_OK)
def get_books_by_rating(book_rating: int = Query(gt=0, lt=6)):
    filtered_books = []
    for book in BOOKS:
        if book.rating == book_rating:
            filtered_books.append(book.dict())
    return filtered_books

@app.get("/books/published/filter", status_code=status.HTTP_200_OK)
def get_books_by_publish_date(year: int = Query(gt=999, lt=10000)):
    filtered_books = []
    for book in BOOKS:
        if book.publish_date == year:
            filtered_books.append(book.dict())
    return filtered_books

@app.post("/create-book", status_code=status.HTTP_201_CREATED)
def create_book(book_request: BookRequest):
    book_data = book_request.model_dump()
    book_data.pop('id', None)
    new_book = Book(id=None, **book_data)
    BOOKS.append(set_book_id(new_book))
    return new_book.dict()

@app.put("/books/update_book", status_code=status.HTTP_200_OK)
def update_book(book: BookRequest):
    if book.id is None:
        raise HTTPException(status_code=400, detail="Book ID is required for update")
    
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = Book(**book.model_dump())
            return BOOKS[i].dict()
    
    raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/{book_id}", status_code=status.HTTP_200_OK)
def delete_book(book_id: int = Path(gt=0)):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            deleted_book = BOOKS.pop(i)
            return {"message": f"Book '{deleted_book.title}' deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Book not found")