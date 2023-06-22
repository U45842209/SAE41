var new_rdv = document.getElementById("new_rdv");
var tableau = document.getElementById("tableau");
var bouton1=document.getElementById("bouton1");
var bouton2=document.getElementById("bouton2");

    function hideTableau(){

        tableau.classList.add("cache");
        new_rdv.classList.remove("cache");
    }

    function hideNew_rdv(){

        new_rdv.classList.add("cache");
        tableau.classList.remove("cache");
    }




    bouton1.addEventListener("click",function(){
        
        hideTableau();
    });

    bouton2.addEventListener("click",function(){
        
        hideNew_rdv();
    });


