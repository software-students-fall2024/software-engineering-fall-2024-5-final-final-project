let menuIcon = document.querySelector("#menu-icon");
let navbar = document.querySelector(".navbar");
let sections = document.querySelectorAll("section");
let navLinks = document.querySelectorAll("header nav a");

// Direct to clicked tab
window.onscroll = () => {
    selections.forEeach(sec => {
        let top = window.scrollY;
        let offset = sec.offsetTop - 150;
        let height = sec.offsetHeight;
        let id = sec.getAttribute("id");

        if (top >= offset && top < offset + height) {
            navLinks.forEach(links => {
                links.classList.remove("active");
                document.querySelector("header nav a [href*=" + id + " ]").classList.add("active");
            })
        }
    })
}

menuIcon.onclick = () => {
    menuIcon.classList.toggle("bx-x");
    navbar.classList.toggle("active");
}

document.getElementById('menu-icon').addEventListener('click', function() {
    var navbar = document.querySelector('.navbar');
    if (navbar.style.display === 'block') {
        navbar.style.display = 'none';
    } else {
        navbar.style.display = 'block';
    }
});

// "Action" cell in table
function handleAction(selectElement, barId) {
    const action = selectElement.value; // get selected action

    if (action === "add") {window.location.href = "/add";}                     // direct to add.html 
    else if (action === "edit") {window.location.href = `/edit/${barId}`;}     // direct to add.html 
    else if (action === "delete") {window.location.href = `/delete/${barId}`;} // direct to add.html
}