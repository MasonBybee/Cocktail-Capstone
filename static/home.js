const searchbar = document.querySelector(".homeSearch");
const resultContainer = document.querySelector(".resultContainer");

function debouncer(func, timeout = 300) {
  let timeoutID;
  return (...args) => {
    clearTimeout(timeoutID);
    timeoutID = setTimeout(() => {
      func.apply(this, args);
    }, timeout);
  };
}

async function searchOnBackend(query) {
  const backendEndpoint = "/search?query=" + encodeURIComponent(query);
  if (searchbar.value === "") {
    resultContainer.innerHTML = "";
    return;
  }
  try {
    const response = await axios.get(backendEndpoint);
    resultContainer.innerHTML = "";
    const drinks = JSON.parse(response.data[0]);
    const ingredients = JSON.parse(response.data[1]);
    console.log(ingredients);
    // Make this a function to reduce duplication
    if (ingredients.ingredients) {
      for (const ingredient of ingredients.ingredients) {
        const link = document.createElement("a");
        link.classList.add("text-decoration-none", "d-table-cell");
        link.href = `/ingredients/${ingredient.strIngredient}`;

        const customCard = document.createElement("div");
        customCard.style.width = "18rem";
        customCard.classList.add("card", "m-3", "cocktailCard", "customCard");

        const img = document.createElement("img");
        img.classList.add("card-img-top");
        img.src = `https://www.thecocktaildb.com/images/ingredients/${ingredient.strIngredient}-medium.png`;
        img.alt = ingredient.strIngredient;

        const div = document.createElement("div");
        div.classList.add("card-body", "cocktailCard");

        const h5 = document.createElement("h5");
        h5.classList.add("card-title", "cocktailTitle");
        h5.textContent = ingredient.strIngredient;

        div.append(h5);
        customCard.append(img);
        customCard.append(div);
        link.append(customCard);

        resultContainer.append(link);
      }
    }
    if (drinks.drinks)
      for (const drink of drinks.drinks) {
        const link = document.createElement("a");
        link.classList.add("text-decoration-none", "d-table-cell");
        link.href = `/cocktails/${drink.idDrink}`;

        const customCard = document.createElement("div");
        customCard.style.width = "18rem";
        customCard.classList.add("card", "m-3", "cocktailCard", "customCard");

        const img = document.createElement("img");
        img.classList.add("card-img-top");
        img.src = drink.strDrinkThumb;
        img.alt = drink.strDrink;

        const div = document.createElement("div");
        div.classList.add("card-body", "cocktailCard");

        const h5 = document.createElement("h5");
        h5.classList.add("card-title", "cocktailTitle");
        h5.textContent = drink.strDrink;

        div.append(h5);
        customCard.append(img);
        customCard.append(div);
        link.append(customCard);

        resultContainer.append(link);
      }
  } catch (error) {
    console.error("Error:", error);
  }
}

const debouncedSearch = debouncer(() => {
  searchOnBackend(searchbar.value);
}, 300);

function handleSearch() {
  debouncedSearch();
}

searchbar.addEventListener("keydown", handleSearch);
