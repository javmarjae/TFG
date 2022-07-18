// When the user clicks anywhere outside of the modal, close it
window.onclick = function (event) {
    if (event.target == document.getElementById('id02')) {
        document.getElementById('id02').style.display = "none";
    }
}