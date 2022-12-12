document.addEventListener("DOMContentLoaded", () => {
    let agreeCheckboxes = document.getElementsByClassName("agree-checkbox");
    for (let checkbox of agreeCheckboxes) {
        checkbox.addEventListener("change", () => {
            let targetId = checkbox.dataset.target;
            let target = document.getElementById(targetId);
            target.disabled = !checkbox.checked;
        });
    }

    let priceFilterInput = document.getElementById("myRange");
    let output = document.getElementById("price");
    if (output) {
        output.innerHTML = "Price starting from " + priceFilterInput?.value + "$"; // Display the default slider value
    }

    priceFilterInput?.addEventListener("change", filter);

    let forms = document.getElementsByClassName('needs-validation');
    // Loop over them and prevent submission
    Array.prototype.filter.call(forms, function (form) {
      form.addEventListener('submit', function (event) {
        if (form.checkValidity() === false) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add('was-validated');
      }, false)
    });

    filter();
})

ALL_BRANDS = 0;

function filterByPrice() {
    let priceFilterInput = document.getElementById("myRange");
    let cars = document.getElementsByClassName("car");
    let price = priceFilterInput.value;
    for (let car of cars) {
        car.hidden = parseFloat(car.dataset.price) < parseFloat(price);
    }
    let output = document.getElementById("price");
    output.innerHTML = "Price starting from " + price + "$";
}

function filterByBrand() {
    let brandFilters = document.getElementsByClassName("brand-filter");
    let checkedBrands = [];
    for (let brand of brandFilters) {
        if (brand.checked) {
            checkedBrands.push(parseInt(brand.value));
        }
    }

    if (checkedBrands.includes(ALL_BRANDS)) {
        return;
    }

    let cars = document.getElementsByClassName("car");
    for (let car of cars) {
        if (!checkedBrands.includes(parseInt(car.dataset.brand))) {
            car.hidden = true;
        }
    }
}

function filter() {
    filterByPrice();
    filterByBrand();
}
