
//                                                       percent
const percent = document.querySelector('#percent')
if (percent.dataset.percent < 50) {
    percent.classList.add("bg-danger")
}
else if (percent.dataset.percent > 84) {
    percent.classList.add("bg-success")

}
percent.addEventListener('click', () => {
    if (percent.classList.contains("progress-bar-animated")) {
        percent.classList.remove("progress-bar-animated")
    }
    else {
        percent.classList.add("progress-bar-animated")
    }
})


//                                                       rows
var yearDivs = document.querySelectorAll('.year');

for (var i = 1; i < yearDivs.length; i++) {
    var toggleIcon = yearDivs[i].querySelector('.toggle-icon');
    var targetId = toggleIcon.getAttribute('data-toggle');
    var target = document.getElementById(targetId);

    target.classList.remove('show');
    target.classList.add('collapse'); 
    toggleIcon.innerHTML = '<i class="fas fa-eye-slash"></i>';
    document.querySelector(`#${targetId}`).style.display = "none"
}


yearDivs.forEach(year => {
    year.addEventListener('click', hide_year);

})
document.querySelectorAll('.month').forEach(month => {
    month.addEventListener('click', hide_rows);

})


function hide_year() {
    let year = document.querySelector(`#${this.dataset.code}`)
    var icon = document.querySelector(`.toggle-icon[data-toggle="${this.dataset.code}"] i`);

    if (year.style.display === "none") {
        year.style.display = "table-row-group";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");

    }
    else {
        year.style.display = "none";
        year.scrollIntoView({ behavior: 'smooth' });

        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");

    }

}


function hide_rows() {
    var icon = document.querySelector(`.toggle-icon[data-toggle="${this.dataset.code}"] i`);

    document.querySelectorAll(`.${this.dataset.code}`).forEach(row => {

    if (row.style.display === "none") {
        row.style.display = "table-row";   
        icon.classList.remove("fa-angle-up");
        icon.classList.add("fa-angle-down");

    }

    else {        
        row.style.display = "none";
        row.parentElement.scrollIntoView({ behavior: 'smooth' });
        icon.classList.remove("fa-angle-down");
        icon.classList.add("fa-angle-up");

    }

    
})

}

//                                                       end rows



