from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from database import Base, engine
from routers import products, reviews, cart, wishlist, search, auth

# ✅ Initialize FastAPI app
app = FastAPI()

# ✅ Define OAuth2 security scheme for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ✅ Enable CORS for frontend communication (Use frontend domain when deployed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow local frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
app.include_router(cart.router, prefix="/cart", tags=["Shopping Cart"])
app.include_router(wishlist.router, prefix="/wishlist", tags=["Wishlist"])
app.include_router(search.router, prefix="/search", tags=["Search"])

# ✅ Root endpoint
@app.get("/")
def home():
    return {"message": "Welcome to TimeSwap - The Barter Marketplace!"}
