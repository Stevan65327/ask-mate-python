let navBar = document.getElementsByClassName("top-nav-bar")[0];
console.log(navBar);
let subItems = navBar.getElementsByClassName("subitem")
console.log(subItems);
for (let i = 0; i < subItems.length; i++) {
    console.log(subItems[i].innerText)
    if (subItems[i].innerText === "Registration")
    {alert("Registration")
    subItems[i].style.display = "none"
    }

}