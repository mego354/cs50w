const disc = document.querySelector('#discount_id')
const new_disc = document.querySelector('#new_discount_id')
const new_discount_caption = document.querySelector('#new_discount_caption')

if (disc.dataset.persent < '1') {
  disc.innerHTML = "Add a discount";
}
disc.addEventListener('click', () => {
  new_discount_caption.style.display = "table-caption";
  disc.style.display = "none";
})




document.querySelectorAll('.delete_item').forEach(link => {
  link.addEventListener('click', check)
})



function updateMaxQuantity(input, currentQuantity, maxStock) {
    var newMax = parseInt(currentQuantity) + parseInt(maxStock);
    input.setAttribute('max', newMax);
  }


function check() {
  this.innerHTML = "تم" 

}



