let currentUser = null;
let vendors = [];
let selectedVendor = null;
let cart = [];

// Attach Event Listeners once DOM loads
document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("login-form");
  const checkoutForm = document.getElementById("checkout-form");

  if (loginForm) {
    loginForm.addEventListener("submit", handleLogin);
  }
  if (checkoutForm) {
    checkoutForm.addEventListener("submit", handleCheckout);
  }

  // Check active session on load
  fetch('/api/user')
    .then(res => res.json())
    .then(data => {
      if (data.logged_in) {
        currentUser = data.user;
        showApp();
      }
    })
    .catch(err => console.error("Session check failed:", err));
});

// Handle Login Form Submission
function handleLogin(e) {
  e.preventDefault();
  
  const name = document.getElementById("login-name").value;
  const email = document.getElementById("login-email").value;

  fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      currentUser = data.user;
      showApp();
    } else {
      alert("Sign in failed. Please try again.");
    }
  })
  .catch(err => console.error("Login request failed:", err));
}

function handleLogout() {
  fetch('/api/logout', { method: 'POST' })
    .then(() => {
      currentUser = null;
      cart = [];
      document.getElementById("app-screen").style.display = "none";
      document.getElementById("auth-screen").style.display = "flex";
    });
}

function showApp() {
  document.getElementById("auth-screen").style.display = "none";
  document.getElementById("app-screen").style.display = "block";
  document.getElementById("user-greeting").innerText = `Welcome, ${currentUser.name}!`;
  document.getElementById("cust-name").value = currentUser.name;
  loadVendors();
}

function loadVendors() {
  fetch('/api/vendors')
    .then(res => res.json())
    .then(data => {
      vendors = data;
      renderVendors();
      if (vendors.length > 0) selectVendor(vendors[0].id);
    });
}

function renderVendors() {
  const container = document.getElementById("vendor-list");
  container.innerHTML = "";

  vendors.forEach((vendor, index) => {
    const card = document.createElement("div");
    card.className = `vendor-card ${selectedVendor && selectedVendor.id === vendor.id ? 'active' : ''}`;
    card.onclick = () => selectVendor(vendor.id);

    card.innerHTML = `
      <h4>${vendor.name} ${index === 0 ? '⭐ (Nearest)' : ''}</h4>
      <p>Delivery Fee: ₱${vendor.deliveryFee.toFixed(2)}</p>
      <span class="distance-badge">📍 ${vendor.distanceKm} km away</span>
    `;
    container.appendChild(card);
  });
}

function selectVendor(vendorId) {
  selectedVendor = vendors.find(v => v.id === vendorId);
  renderVendors();
  renderProducts();

  document.getElementById("current-vendor-title").innerText = selectedVendor.name + " Menu (20 Items)";
  document.getElementById("current-vendor-distance").innerText = `📍 ${selectedVendor.distanceKm} km away`;
}

function renderProducts() {
  const container = document.getElementById("product-list");
  container.innerHTML = "";

  selectedVendor.products.forEach(prod => {
    const card = document.createElement("div");
    card.className = "product-card";
    card.innerHTML = `
      <div>
        <h4>${prod.name}</h4>
        <p>${prod.desc}</p>
      </div>
      <div class="product-bottom">
        <span class="price">₱${prod.price.toFixed(2)}</span>
        <button class="add-btn" onclick="addToCart(${prod.id})">+ Add</button>
      </div>
    `;
    container.appendChild(card);
  });
}

function addToCart(productId) {
  const product = selectedVendor.products.find(p => p.id === productId);
  const existingItem = cart.find(item => item.id === productId);

  if (existingItem) {
    existingItem.qty += 1;
  } else {
    cart.push({ ...product, qty: 1 });
  }

  updateCartUI();
}

function updateCartUI() {
  const cartItemsContainer = document.getElementById("cart-items");
  const totalQty = cart.reduce((sum, item) => sum + item.qty, 0);
  document.getElementById("cart-count").innerText = totalQty;

  if (cart.length === 0) {
    cartItemsContainer.innerHTML = `<p class="empty-msg">Your cart is empty.</p>`;
    document.getElementById("cart-subtotal").innerText = "₱0.00";
    document.getElementById("cart-delivery-fee").innerText = "₱0.00";
    document.getElementById("cart-total").innerText = "₱0.00";
    return;
  }

  cartItemsContainer.innerHTML = "";
  let subtotal = 0;

  cart.forEach(item => {
    const itemTotal = item.price * item.qty;
    subtotal += itemTotal;
    cartItemsContainer.innerHTML += `
      <div class="cart-item">
        <div><strong>${item.name}</strong> x ${item.qty}</div>
        <div>₱${itemTotal.toFixed(2)}</div>
      </div>`;
  });

  const deliveryFee = selectedVendor.deliveryFee;
  const grandTotal = subtotal + deliveryFee;

  document.getElementById("cart-subtotal").innerText = `₱${subtotal.toFixed(2)}`;
  document.getElementById("cart-delivery-fee").innerText = `₱${deliveryFee.toFixed(2)}`;
  document.getElementById("cart-total").innerText = `₱${grandTotal.toFixed(2)}`;
}

function toggleCart() {
  const modal = document.getElementById("cart-modal");
  modal.style.display = modal.style.display === "flex" ? "none" : "flex";
}

function handleCheckout(e) {
  e.preventDefault();
  if (cart.length === 0) return alert("Cart is empty!");

  const name = document.getElementById("cust-name").value;
  const address = document.getElementById("cust-address").value;
  const time = document.getElementById("cust-time").value;

  const subtotal = cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
  const total = subtotal + selectedVendor.deliveryFee;

  fetch('/api/checkout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      vendor_id: selectedVendor.id,
      name,
      address,
      time,
      total,
      cart
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      toggleCart();
      document.getElementById("confirmation-details").innerHTML = `
        Thank you, <strong>${data.order.customer_name}</strong>!<br/>
        Order ID: <strong>#${data.order.order_id}</strong><br/>
        Vendor: <strong>${data.order.vendor_name}</strong><br/>
        Delivery Time: <strong>${data.order.delivery_time}</strong>
      `;
      document.getElementById("confirm-modal").style.display = "flex";
      cart = [];
      updateCartUI();
      document.getElementById("checkout-form").reset();
    }
  });
}

function closeConfirmation() {
  document.getElementById("confirm-modal").style.display = "none";
}

function toggleLogsModal() {
  const modal = document.getElementById("logs-modal");
  if (modal.style.display === "flex") {
    modal.style.display = "none";
  } else {
    fetch('/api/customer-logs')
      .then(res => res.json())
      .then(logs => {
        const tbody = document.getElementById("logs-table-body");
        tbody.innerHTML = "";
        logs.forEach(log => {
          tbody.innerHTML += `
            <tr>
              <td>#${log.order_id}</td>
              <td><strong>${log.customer_name}</strong></td>
              <td>${log.address}</td>
              <td>${log.vendor_name}</td>
              <td>${log.items}</td>
              <td>₱${log.total_amount.toFixed(2)}</td>
              <td>${log.delivery_time}</td>
              <td><span class="status-badge">${log.status}</span></td>
            </tr>
          `;
        });
        modal.style.display = "flex";
      });
  }
}