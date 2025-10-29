from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine, SessionLocal
from .models import Feedback
from openai import OpenAI

Base.metadata.create_all(bind=engine)
app = FastAPI()
client = OpenAI(api_key="8cf3238b6d70b97357059d90e41f6fd8")  # Replace with your key

# CORS setup so frontend can talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/submit/")
def submit_feedback(teacher: str = Form(...), rating: int = Form(...), comment: str = Form(...)):
    db = SessionLocal()
    new_feedback = Feedback(teacher=teacher, rating=rating, comment=comment)
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    db.close()
    return {"message": "Feedback submitted successfully"}

@app.get("/summary/{teacher}")
def summarize_feedback(teacher: str):
    db = SessionLocal()
    feedbacks = db.query(Feedback).filter(Feedback.teacher == teacher).all()
    db.close()

    if not feedbacks:
        return {"summary": "No feedback yet."}

    comments = [f.comment for f in feedbacks]
    prompt = f"Summarize the following feedbacks for teacher {teacher}:\n" + "\n".join(comments)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    summary = response.choices[0].message.content

    avg_rating = sum(f.rating for f in feedbacks) / len(feedbacks)


    return {"teacher": teacher, "summary": summary, "avg_rating": round(avg_rating, 2)}
