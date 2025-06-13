import sys
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from py_allrecipes import search_recipes, get_recipe

console = Console()


def view_saved_recipes():
    import os
    import json
    save_dir = os.path.join(os.path.dirname(__file__), "saved_recipes")
    if not os.path.exists(save_dir):
        console.print("[yellow]No saved recipes found.[/yellow]")
        return
    files = [f for f in os.listdir(save_dir) if f.endswith(".json")]
    if not files:
        console.print("[yellow]No saved recipes found.[/yellow]")
        return
    table = Table(title="Saved Recipes", show_lines=True)
    table.add_column("#", style="cyan", width=4)
    table.add_column("Filename", style="bold")
    for idx, fname in enumerate(files, 1):
        table.add_row(str(idx), fname)
    console.print(table)
    choice = Prompt.ask(
        "Select a recipe number to view",
        choices=[str(i) for i in range(1, len(files) + 1)],
    )
    selected_file = files[int(choice) - 1]
    with open(os.path.join(save_dir, selected_file), "r", encoding="utf-8") as f:
        details = json.load(f)
    console.print(Panel(Text(details["title"], style="bold yellow"), title="Recipe Title"))
    console.print(Panel("\n".join(details["ingredients"]), title="Ingredients", style="green"))
    console.print(Panel("\n".join(details["steps"]), title="Steps", style="blue"))
    info = details["details"]
    info_text = f"Prep: {info.get('prep_time', '-')} | Cook: {info.get('cook_time', '-')} | Total: {info.get('total_time', '-')} | Servings: {info.get('servings', '-')} | Yield: {info.get('yield', '-')}"
    console.print(Panel(info_text, title="Info", style="magenta"))


def main():
    console.print("[bold green]Welcome to Terminal Cook![/bold green]")
    mode = Prompt.ask("Choose an option", choices=["search", "view"], default="search")
    if mode == "view":
        view_saved_recipes()
        return
    query = Prompt.ask("Enter a recipe search term")
    try:
        recipes = search_recipes(query)
    except Exception as e:
        console.print(f"[red]Error searching recipes:[/red] {e}")
        sys.exit(1)
    if not recipes:
        console.print("[yellow]No recipes found.[/yellow]")
        sys.exit(0)

    table = Table(title="Search Results", show_lines=True)
    table.add_column("#", style="cyan", width=4)
    table.add_column("Title", style="bold")
    table.add_column("Ratings", style="magenta")
    for idx, recipe in enumerate(recipes[:10], 1):
        ratings = str(recipe.get("ratings", "-"))
        table.add_row(str(idx), recipe["title"], ratings)
    console.print(table)

    choice = Prompt.ask(
        "Select a recipe number to view",
        choices=[str(i) for i in range(1, min(11, len(recipes) + 1))],
    )
    selected = recipes[int(choice) - 1]
    try:
        details = get_recipe(selected["url"])
    except Exception as e:
        console.print(f"[red]Error fetching recipe details:[/red] {e}")
        sys.exit(1)

    console.print(
        Panel(Text(details["title"], style="bold yellow"), title="Recipe Title")
    )
    console.print(
        Panel("\n".join(details["ingredients"]), title="Ingredients", style="green")
    )
    console.print(Panel("\n".join(details["steps"]), title="Steps", style="blue"))
    info = details["details"]
    info_text = f"Prep: {info.get('prep_time', '-')} | Cook: {info.get('cook_time', '-')} | Total: {info.get('total_time', '-')} | Servings: {info.get('servings', '-')} | Yield: {info.get('yield', '-')}"
    console.print(Panel(info_text, title="Info", style="magenta"))

    # Ask if user wants to save the recipe
    save_choice = Prompt.ask("Do you want to save this recipe?", choices=["y", "n"], default="n")
    if save_choice == "y":
        import json
        import os
        save_dir = os.path.join(os.path.dirname(__file__), "saved_recipes")
        os.makedirs(save_dir, exist_ok=True)
        filename = details["title"].replace(" ", "_").replace("/", "-") + ".json"
        filepath = os.path.join(save_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(details, f, ensure_ascii=False, indent=2)
        console.print(f"[green]Recipe saved to {filepath}[/green]")


if __name__ == "__main__":
    main()
