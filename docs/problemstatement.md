# Problem Statement: AI-Powered Restaurant Recommendation System (Zomato Use Case)

Build an AI-powered restaurant recommendation service inspired by Zomato.  
The system should combine structured restaurant data with a Large Language Model (LLM) to deliver personalized and explainable suggestions based on user preferences.

## Objective

Design and implement an application that can:

- Accept user preferences such as location, budget, cuisine, and minimum rating
- Use a real-world restaurant dataset
- Generate personalized, human-like recommendations with an LLM
- Present results clearly in a user-friendly format

## System Workflow

### 1) Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face:  
  [https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- Extract and normalize key fields, including:
  - Restaurant name
  - Location
  - Cuisine
  - Cost
  - Rating

### 2) User Input

Collect user preferences such as:

- Location (for example: Delhi, Bangalore)
- Budget (low, medium, high)
- Cuisine preference (for example: Italian, Chinese)
- Minimum acceptable rating
- Additional needs (for example: family-friendly, quick service)

### 3) Integration Layer

- Filter the dataset based on user criteria
- Prepare shortlisted restaurant records as structured context
- Feed this context into an LLM prompt
- Use prompt design that helps the model compare, reason, and rank options

### 4) Recommendation Engine

Use the LLM to:

- Rank restaurants by relevance to user preferences
- Explain why each recommendation is a good match
- Optionally provide a short comparative summary of top choices

### 5) Output Display

Present top recommendations in a clean and readable format, including:

- Restaurant name
- Cuisine
- Rating
- Estimated cost
- AI-generated explanation
