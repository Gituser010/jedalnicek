#!/usr/bin/env python3
"""
Recipe Viewer Web Application
A simple web application to browse and view recipes from a JSON file.
"""

import json
from pathlib import Path
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recipe Viewer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .main-content {
            display: flex;
            min-height: 600px;
        }

        .sidebar {
            width: 350px;
            background: #f8f9fa;
            border-right: 1px solid #e0e0e0;
            padding: 20px;
            overflow-y: auto;
            max-height: 700px;
        }

        .search-box {
            margin-bottom: 20px;
        }

        .search-box input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            transition: border-color 0.3s;
        }

        .search-box input:focus {
            outline: none;
            border-color: #667eea;
        }

        .recipe-list {
            list-style: none;
        }

        .recipe-item {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            border: 2px solid transparent;
        }

        .recipe-item:hover {
            transform: translateX(5px);
            border-color: #667eea;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
        }

        .recipe-item.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .recipe-item-name {
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 5px;
        }

        .recipe-item-cuisine {
            font-size: 12px;
            opacity: 0.8;
        }

        .recipe-details {
            flex: 1;
            padding: 40px;
            overflow-y: auto;
            max-height: 700px;
        }

        .recipe-details-empty {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: #999;
            font-size: 1.2em;
        }

        .recipe-title {
            font-size: 2.5em;
            color: #333;
            margin-bottom: 20px;
        }

        .recipe-meta {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }

        .meta-badge {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 14px;
            font-weight: 600;
        }

        .badge-cuisine {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .badge-difficulty {
            background: #e0e0e0;
            color: #333;
        }

        .meta-item {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #666;
            font-size: 14px;
        }

        .section {
            margin-top: 40px;
        }

        .section-title {
            font-size: 1.8em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }

        .ingredients-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 10px;
        }

        .ingredient-item {
            padding: 12px 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }

        .instructions-list {
            counter-reset: step-counter;
        }

        .instruction-item {
            padding: 20px;
            margin-bottom: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            position: relative;
            padding-left: 60px;
        }

        .instruction-item::before {
            counter-increment: step-counter;
            content: counter(step-counter);
            position: absolute;
            left: 20px;
            top: 20px;
            width: 30px;
            height: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }

        @media (max-width: 768px) {
            .main-content {
                flex-direction: column;
            }

            .sidebar {
                width: 100%;
                border-right: none;
                border-bottom: 1px solid #e0e0e0;
                max-height: 300px;
            }

            .recipe-details {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍳 Recipe Viewer</h1>
            <p>Discover and explore delicious recipes</p>
        </div>
        <div class="main-content">
            <div class="sidebar">
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="🔍 Search recipes...">
                </div>
                <ul class="recipe-list" id="recipeList"></ul>
            </div>
            <div class="recipe-details" id="recipeDetails">
                <div class="recipe-details-empty">
                    Select a recipe to view details
                </div>
            </div>
        </div>
    </div>

    <script>
        let recipes = [];
        let selectedRecipeId = null;

        // Fetch recipes from API
        async function loadRecipes() {
            try {
                const response = await fetch('/api/recipes');
                recipes = await response.json();
                renderRecipeList();
                if (recipes.length > 0) {
                    selectRecipe(0);
                }
            } catch (error) {
                console.error('Error loading recipes:', error);
            }
        }

        // Render recipe list
        function renderRecipeList(filter = '') {
            const recipeList = document.getElementById('recipeList');
            const filteredRecipes = recipes.filter(recipe =>
                recipe.name.toLowerCase().includes(filter.toLowerCase()) ||
                recipe.cuisine.toLowerCase().includes(filter.toLowerCase())
            );

            recipeList.innerHTML = filteredRecipes.map((recipe, index) => `
                <li class="recipe-item ${selectedRecipeId === index ? 'active' : ''}"
                    onclick="selectRecipe(${index})">
                    <div class="recipe-item-name">${recipe.name}</div>
                    <div class="recipe-item-cuisine">🍽️ ${recipe.cuisine}</div>
                </li>
            `).join('');
        }

        // Select and display recipe
        function selectRecipe(index) {
            selectedRecipeId = index;
            const recipe = recipes[index];
            renderRecipeList(document.getElementById('searchInput').value);
            displayRecipe(recipe);
        }

        // Display recipe details
        function displayRecipe(recipe) {
            const details = document.getElementById('recipeDetails');
            details.innerHTML = `
                <h1 class="recipe-title">${recipe.name}</h1>
                <div class="recipe-meta">
                    <span class="meta-badge badge-cuisine">🍽️ ${recipe.cuisine}</span>
                    <span class="meta-badge badge-difficulty">📊 ${recipe.difficulty}</span>
                    <div class="meta-item">⏱️ Prep: ${recipe.prep_time}</div>
                    <div class="meta-item">🔥 Cook: ${recipe.cook_time}</div>
                    <div class="meta-item">👥 Servings: ${recipe.servings}</div>
                </div>

                <div class="section">
                    <h2 class="section-title">🛒 Ingredients</h2>
                    <div class="ingredients-list">
                        ${recipe.ingredients.map(ingredient => `
                            <div class="ingredient-item">${ingredient}</div>
                        `).join('')}
                    </div>
                </div>

                <div class="section">
                    <h2 class="section-title">📝 Instructions</h2>
                    <div class="instructions-list">
                        ${recipe.instructions.map(instruction => `
                            <div class="instruction-item">${instruction}</div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        // Search functionality
        document.getElementById('searchInput').addEventListener('input', (e) => {
            renderRecipeList(e.target.value);
        });

        // Load recipes on page load
        loadRecipes();
    </script>
</body>
</html>
"""

def load_recipes():
    """Load recipes from JSON file."""
    recipe_file = Path(__file__).parent / "recipes.json"
    try:
        with open(recipe_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading recipes: {e}")
        return []

@app.route('/')
def index():
    """Render the main page."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/recipes')
def get_recipes():
    """API endpoint to get all recipes."""
    recipes = load_recipes()
    return jsonify(recipes)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🍳 Recipe Viewer Web Application")
    print("="*50)
    print("\nStarting server...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
