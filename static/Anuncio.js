function denunciar(){
    document.getElementById("abobora").style.display = "block"
    document.getElementById("banana").style.display = "block"
}

function enviardenuncia(){
   if (document.getElementById("caixadetexto").value == ""){
        alert("É necessário escrever uma descrição!")
    }else{
        alert("Denúncia enviada!")
    }
    return;
}

function fechar(){
    document.getElementById("abobora").style.display = "none"
    document.getElementById("banana").style.display = "none"
}
