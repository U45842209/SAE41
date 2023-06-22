var new_rdv = document.getElementById("new_rdv");
var tableau = document.getElementById("tableau");
var bouton1=document.getElementById("bouton1");
var bouton2=document.getElementById("bouton2");
var join_rdv = document.getElementById("form_join");

    function hideTableau(){

        tableau.classList.add("cache");
        new_rdv.classList.remove("cache");
        join_rdv.classList.add("cache");
    }

    function hideNew_rdv(){

        new_rdv.classList.add("cache");
        tableau.classList.remove("cache");
        join_rdv.classList.remove("cache");
    }




    bouton1.addEventListener("click",function(){
        
        hideTableau();
    });

    bouton2.addEventListener("click",function(){
        
        hideNew_rdv();
    });

