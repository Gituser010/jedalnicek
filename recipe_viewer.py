#!/usr/bin/env python3
"""
Recipe Viewer Application
A simple GUI application to browse and view recipes from a JSON file.
"""

import json
import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path


class RecipeViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Recipe Viewer")
        self.root.geometry("1000x700")

        # Load recipes
        self.recipes = self.load_recipes()

        # Configure style
        self.setup_styles()

        # Create UI
        self.create_widgets()

        # Load first recipe if available
        if self.recipes:
            self.recipe_listbox.selection_set(0)
            self.show_recipe(0)

    def load_recipes(self):
        """Load recipes from JSON file."""
        recipe_file = Path(__file__).parent / "recipes.json"
        try:
            with open(recipe_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {recipe_file} not found!")
            return []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {recipe_file}")
            return []

    def setup_styles(self):
        """Configure the application style."""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors
        self.bg_color = "#f5f5f5"
        self.fg_color = "#333333"
        self.accent_color = "#4CAF50"
        self.hover_color = "#e0e0e0"

        self.root.configure(bg=self.bg_color)

    def create_widgets(self):
        """Create and layout all UI widgets."""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - Recipe list
        left_frame = tk.Frame(main_frame, bg=self.bg_color)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))

        # Title for recipe list
        list_title = tk.Label(
            left_frame,
            text="Recipes",
            font=("Arial", 16, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        list_title.pack(pady=(0, 10))

        # Search box
        search_frame = tk.Frame(left_frame, bg=self.bg_color)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(search_frame, text="Search:", bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_recipes)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        # Recipe listbox
        listbox_frame = tk.Frame(left_frame, bg="white", relief=tk.SUNKEN, bd=1)
        listbox_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.recipe_listbox = tk.Listbox(
            listbox_frame,
            font=("Arial", 11),
            bg="white",
            fg=self.fg_color,
            selectmode=tk.SINGLE,
            activestyle='none',
            highlightthickness=0,
            selectbackground=self.accent_color,
            selectforeground="white",
            yscrollcommand=scrollbar.set,
            width=30
        )
        self.recipe_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.recipe_listbox.yview)

        # Bind selection event
        self.recipe_listbox.bind('<<ListboxSelect>>', self.on_recipe_select)

        # Populate recipe list
        self.populate_recipe_list()

        # Right panel - Recipe details
        right_frame = tk.Frame(main_frame, bg="white", relief=tk.SUNKEN, bd=1)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Scrollable recipe details
        canvas = tk.Canvas(right_frame, bg="white", highlightthickness=0)
        scrollbar_right = tk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        self.recipe_details_frame = tk.Frame(canvas, bg="white")

        self.recipe_details_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.recipe_details_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_right.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_right.pack(side="right", fill="y")

        # Bind mousewheel for scrolling
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def populate_recipe_list(self, filter_text=""):
        """Populate the recipe listbox with recipe names."""
        self.recipe_listbox.delete(0, tk.END)

        for recipe in self.recipes:
            if filter_text.lower() in recipe['name'].lower() or \
               filter_text.lower() in recipe['cuisine'].lower():
                self.recipe_listbox.insert(tk.END, recipe['name'])

    def filter_recipes(self, *args):
        """Filter recipes based on search text."""
        filter_text = self.search_var.get()
        self.populate_recipe_list(filter_text)

    def on_recipe_select(self, event):
        """Handle recipe selection from listbox."""
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            # Find the actual recipe index based on filtered list
            selected_name = self.recipe_listbox.get(index)
            for i, recipe in enumerate(self.recipes):
                if recipe['name'] == selected_name:
                    self.show_recipe(i)
                    break

    def show_recipe(self, index):
        """Display the selected recipe details."""
        # Clear previous content
        for widget in self.recipe_details_frame.winfo_children():
            widget.destroy()

        recipe = self.recipes[index]

        # Add padding frame
        content_frame = tk.Frame(self.recipe_details_frame, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Recipe name
        name_label = tk.Label(
            content_frame,
            text=recipe['name'],
            font=("Arial", 20, "bold"),
            bg="white",
            fg=self.accent_color,
            wraplength=600,
            justify=tk.LEFT
        )
        name_label.pack(anchor="w", pady=(0, 10))

        # Cuisine badge
        info_frame = tk.Frame(content_frame, bg="white")
        info_frame.pack(anchor="w", pady=(0, 15))

        cuisine_label = tk.Label(
            info_frame,
            text=f"🍽️  {recipe['cuisine']}",
            font=("Arial", 10),
            bg=self.accent_color,
            fg="white",
            padx=10,
            pady=5
        )
        cuisine_label.pack(side=tk.LEFT, padx=(0, 10))

        difficulty_label = tk.Label(
            info_frame,
            text=f"📊 {recipe['difficulty']}",
            font=("Arial", 10),
            bg=self.hover_color,
            fg=self.fg_color,
            padx=10,
            pady=5
        )
        difficulty_label.pack(side=tk.LEFT)

        # Time and servings info
        meta_frame = tk.Frame(content_frame, bg="white")
        meta_frame.pack(anchor="w", pady=(0, 20), fill=tk.X)

        meta_items = [
            ("⏱️ Prep Time:", recipe['prep_time']),
            ("🔥 Cook Time:", recipe['cook_time']),
            ("👥 Servings:", str(recipe['servings']))
        ]

        for label, value in meta_items:
            item_frame = tk.Frame(meta_frame, bg="white")
            item_frame.pack(anchor="w", pady=2)

            tk.Label(
                item_frame,
                text=label,
                font=("Arial", 10, "bold"),
                bg="white",
                fg=self.fg_color
            ).pack(side=tk.LEFT)

            tk.Label(
                item_frame,
                text=value,
                font=("Arial", 10),
                bg="white",
                fg=self.fg_color
            ).pack(side=tk.LEFT, padx=(5, 0))

        # Separator
        tk.Frame(content_frame, height=2, bg=self.hover_color).pack(fill=tk.X, pady=15)

        # Ingredients section
        ingredients_label = tk.Label(
            content_frame,
            text="🛒 Ingredients",
            font=("Arial", 14, "bold"),
            bg="white",
            fg=self.fg_color
        )
        ingredients_label.pack(anchor="w", pady=(0, 10))

        for ingredient in recipe['ingredients']:
            ingredient_frame = tk.Frame(content_frame, bg="white")
            ingredient_frame.pack(anchor="w", pady=2, fill=tk.X)

            bullet = tk.Label(
                ingredient_frame,
                text="•",
                font=("Arial", 12),
                bg="white",
                fg=self.accent_color
            )
            bullet.pack(side=tk.LEFT, padx=(10, 5))

            tk.Label(
                ingredient_frame,
                text=ingredient,
                font=("Arial", 11),
                bg="white",
                fg=self.fg_color,
                wraplength=550,
                justify=tk.LEFT
            ).pack(side=tk.LEFT, anchor="w")

        # Separator
        tk.Frame(content_frame, height=2, bg=self.hover_color).pack(fill=tk.X, pady=15)

        # Instructions section
        instructions_label = tk.Label(
            content_frame,
            text="📝 Instructions",
            font=("Arial", 14, "bold"),
            bg="white",
            fg=self.fg_color
        )
        instructions_label.pack(anchor="w", pady=(0, 10))

        for i, instruction in enumerate(recipe['instructions'], 1):
            instruction_frame = tk.Frame(content_frame, bg="white")
            instruction_frame.pack(anchor="w", pady=5, fill=tk.X)

            step_number = tk.Label(
                instruction_frame,
                text=f"{i}.",
                font=("Arial", 11, "bold"),
                bg="white",
                fg=self.accent_color,
                width=3,
                anchor="w"
            )
            step_number.pack(side=tk.LEFT, padx=(10, 5))

            tk.Label(
                instruction_frame,
                text=instruction,
                font=("Arial", 11),
                bg="white",
                fg=self.fg_color,
                wraplength=540,
                justify=tk.LEFT
            ).pack(side=tk.LEFT, anchor="w")


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = RecipeViewerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
