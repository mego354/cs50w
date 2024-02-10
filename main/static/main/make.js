document.querySelectorAll('.category_header').forEach(category => {
  category.addEventListener('click', hide_category);
})

document.querySelectorAll('.input_card').forEach(input => {
  input.addEventListener('focus', () => {
    if (input.value === "0") {
      input.value = "";
    }
  });
  
  input.addEventListener('blur', () => {
    if (input.value === "") {
      input.value = "0";
    }
  });

  input.addEventListener('mousewheel', (event) => {
    input.blur()

  });

  

  
})

document.querySelectorAll('.stock').forEach(stock => {
  if (stock.dataset.quantity === "0") {
    stock.innerHTML = "غير متوفر";
  }
})
  
  
  function hide_category() {
    var icon = document.querySelector(`.toggle-icon[data-toggle="${this.dataset.code}"] i`);
    category_block = document.querySelector(`#${this.dataset.code}`)
    if(category_block.style.display != "none") {
      category_block.style.display = "none";
      icon.classList.remove("fa-angle-down");
      icon.classList.add("fa-angle-up");

    }
    else {
      category_block.style.display = "flex";
      icon.classList.remove("fa-angle-up");
      icon.classList.add("fa-angle-down");

      
    }
  }


  