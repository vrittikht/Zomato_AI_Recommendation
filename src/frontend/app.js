/**
 * Zomato AI - Frontend Logic
 * Interacts with the FastAPI backend to generate recommendations.
 */

// Priority: 1. window.CONFIG (from Vercel build), 2. Localhost fallback, 3. Hardcoded fallback
const API_BASE_URL = (window.CONFIG && window.CONFIG.API_BASE_URL) 
    ? window.CONFIG.API_BASE_URL 
    : (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000/api/v1'
        : 'https://web-production-20a5a.up.railway.app/api/v1'); 

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('recommendation-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnLoader = document.getElementById('btn-loader');
    const resultsSection = document.getElementById('results');
    const recommendationsContainer = document.getElementById('recommendations-container');
    const aiSummary = document.getElementById('ai-summary');
    const fallbackNotice = document.getElementById('fallback-notice');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Prepare request payload
        const payload = {
            location: document.getElementById('location').value,
            cuisine: document.getElementById('cuisine').value || null,
            budget: document.getElementById('budget').value || null,
            rating: parseFloat(document.getElementById('rating').value) || 0,
            additional_preferences: document.getElementById('additional_preferences').value || null,
            top_k: 6 // Request 6 items for the grid
        };

        // UI State: Loading
        setLoading(true);
        resultsSection.classList.add('hidden');
        
        try {
            const response = await fetch(`${API_BASE_URL}/recommend`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to fetch recommendations');
            }

            const data = await response.json();
            renderResults(data);
            
            // Scroll to results
            resultsSection.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            console.error('Error:', error);
            alert(`Oops! Something went wrong: ${error.message}`);
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            btnLoader.style.display = 'inline-block';
            submitBtn.querySelector('.btn-text').textContent = 'Consulting AI...';
        } else {
            submitBtn.disabled = false;
            btnLoader.style.display = 'none';
            submitBtn.querySelector('.btn-text').textContent = 'Generate Recommendations';
        }
    }

    function renderResults(data) {
        // Clear previous results
        recommendationsContainer.innerHTML = '';
        
        // Set summary
        aiSummary.textContent = data.summary || `Found ${data.recommendations.length} great options for you.`;
        
        // Show/Hide fallback notice
        if (data.used_fallback) {
            fallbackNotice.classList.remove('hidden');
        } else {
            fallbackNotice.classList.add('hidden');
        }

        // Create cards
        data.recommendations.forEach(item => {
            const card = document.createElement('div');
            card.className = 'restaurant-card';
            
            card.innerHTML = `
                <div class="card-header">
                    <span class="rating-badge">${item.rating.toFixed(1)} ★</span>
                    <span class="restaurant-name">${item.name}</span>
                </div>
                <div class="card-body">
                    <span class="cuisine-tags">${item.cuisine}</span>
                    <p class="explanation">"${item.explanation}"</p>
                </div>
                <div class="card-footer">
                    <span class="location">📍 ${item.location}</span>
                    <span class="cost">₹${item.cost} for two</span>
                </div>
            `;
            recommendationsContainer.appendChild(card);
        });

        // Reveal section
        resultsSection.classList.remove('hidden');
    }
});
