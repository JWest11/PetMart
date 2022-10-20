
let images = new Array('static/galleryImages/cheetah.jpg', 'static/galleryImages/elephant.jpg', 'static/galleryImages/possum.jpg', 'static/galleryImages/turtle.jpg', 'static/galleryImages/zebra.jpg');
let i1 = 0;
let i2 = 1;
let cartTotal = 0;


function rotate() {
    $('#gallery1').empty();
    $('#gallery2').empty();
    $('#gallery1').append(`<img src="${images[i1]}" alt="animal">`);
    $('#gallery2').append(`<img src="${images[i2]}" alt="animal">`);
    i1 = i2;
    if (i1 == images.length - 1) {
        i2 = 0;
    } else {
        i2 = i1+1;
    };
    setTimeout(rotate, 8*1000);
};

function addToCart(listingId) {
    let cart = getCookie('cart');
    if (cart) {
        cart += ',' + `${listingId}`;
    } else {
        cart = `${listingId}`;
    }
    document.cookie = `cart=${cart}; max-age=360; path=/;`;
};

function removeFromCart(listingId) {
    let cart = getCookie('cart');
    if (!cart) {return};
    let array = cart.split(',');
    for (let i=0; i<array.length; i++) {
        console.log(Number(array[i]));
        if (Number(array[i]) === listingId) {
            array.splice(i, 1);
        };
    };
    let output = array.join();
    document.cookie = `cart=${output}; max-age=60; path=/;`;

};

function clearCart() {
    document.cookie = 'cart=0; max-age=-1; path=/;';
};

function getCookie(name) {
    let matches = document.cookie.match(new RegExp(
      "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    let output = matches ? decodeURIComponent(matches[1]) : undefined;
    console.log(output);
    return output;
};

function toggleCartButton(elementId) {
    let element = document.getElementById(elementId);
    if (element.classList.contains('active')) {
        element.classList.remove('active');
        return;
    };
    element.classList.add('active');
};

function refreshCartStyle() {
    $('#navCart').empty();
    $('#checkout').empty();
    let cartString = getCookie('cart');
    if (!cartString) {return};
    let cartList = cartString.split(',');
    let cartLength = cartList.length;
    $('#checkout').append('<a class="nav-link" href="/checkout">Checkout</a>');
    $('#navCart').append(`<a class="cart_a" href="/checkout"><div class="cart_container"><img src="../static/miscImages/cartIcon.png" alt="cart"><p>${cartLength}</p></div></a>`);


};

function checkCartButtons() {
    let cart = getCookie('cart');
    if (!cart) {return};
    let array = cart.split(',');
    for (let id of array) {
        toggleCartButton(`${id}`);
    };
};

function createPurchaseForm() {
    let cartString = getCookie('cart');
    $('#purchaseForm').append(`<input type="hidden" value="${cartString}">`);
};

function removeCartDiv(id) {
    $(`#${id}`).remove();
};

function filterCartItems() {
    let cart = getCookie('cart');
    let listings = document.querySelectorAll('.checkout_listing')
    if (!cart) {
        listings.forEach((listing) => {
            $(`#${listing.id}`).remove()
        });
        return
    };
    let array = cart.split(',');
    listings.forEach((listing) => {
        if (!array.includes(listing.id)) {
            $(`#${listing.id}`).remove()
        };
    });
};

function calculateCartTotal() {
    cartTotal = 0
    $('#cartTotal').empty();
    let listings = document.querySelectorAll('[data-price]')
    console.log(listings);
    listings.forEach((listing) => {
        cartTotal += Number(listing.getAttribute('data-price'));
    });
    $('#cartTotal').append(`$${cartTotal}`);
};

function completePurchase() {
    let accountBalance = Number(document.getElementById('accountBalance').getAttribute('data-balance'));
    if (accountBalance < cartTotal) {
        createAlert('Insufficient Funds');
        return;
    };

    let listingIds = [];
    
    document.querySelectorAll('[data-listingid]').forEach((element) => {
        listingIds.push(Number(element.getAttribute('data-listingid')));
    });

    const purchaseUrl = 'http://127.0.0.1:5000/completePurchase';
    
    let jquerryRequest = $.ajax({
        type: "POST",
        url: purchaseUrl,
        data: JSON.stringify({listingIds}),
        dataType: 'json'
    });

    jquerryRequest.done(() => {
        console.log('data successfully sent');
    });

    jquerryRequest.fail((responseText) => {
        console.log(responseText);
        console.log('error');
    });
    
    clearCart();
    filterCartItems();
    refreshCartStyle();
    $('#accountBalance').empty();
    $('#accountBalance').append(`$${accountBalance - cartTotal}`)
    $('#cartTotal').empty();
    $('#cartTotal').append('$0')
    createAlert('Purchase Successful! Check Account');
    
};

function createAlert(message) {
    $('#alerts').empty();
    $('#alerts').append(`<h3>${message}</h3>`);
}

function redirect(url) {
    window.location.replace(`http://127.0.0.1:5000${url}`)
};

$(function() {
    i1 = Math.floor(Math.random()*5);
    $('#gallery2').append(`<img src="${images[i1]}" alt="animal">`);
    if (i1 == images.length - 1) {
        i2 = 0;
    } else {
        i2 = i1+1;
    };
    setTimeout(rotate, 8*1000);
    refreshCartStyle();
    if ($('#shop_page').length) {
        checkCartButtons();
    };
    if ($('#checkout_page').length) {
        createPurchaseForm();
        filterCartItems();
        document.getElementById('cart_container').classList.remove('inactive');
        document.getElementById('cart_total_container').classList.remove('inactive');
        calculateCartTotal();
    };
    
});