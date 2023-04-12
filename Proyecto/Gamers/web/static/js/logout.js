window.onbeforeunload = function(){
    sessionStorage.setItem("is_logout","yes");
};

if(sessionStorage.getItem("is_logout")) {
    fetch("/web/authentication/logout", {method: "GET", headers:{'X_CSRFToken':document.querySelector("meta[name='csrf-token']").getAttribute('content')}});
    sessionStorage.removeItem('is_logout');
};