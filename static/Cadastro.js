    
function limpa_formulário_cep() {
        document.getElementById('cidade').value=("");
        document.getElementById('uf').value=("");
        document.getElementById('bairro').value=("");
}

function meu_callback(conteudo) {
    if (!("erro" in conteudo)) {
        document.getElementById('cidade').value=(conteudo.localidade);
        document.getElementById('uf').value=(conteudo.uf);
        document.getElementById('bairro').value=(conteudo.bairro);
    }
    else {
        limpa_formulário_cep();
        alert("CEP não encontrado.");
    }
}
    
function pesquisacep(valor) {
    var cep = valor.replace(/\D/g, '');

    if (cep != "") {
        var validacep = /^[0-9]{8}$/;

        if(validacep.test(cep)) {
            var script = document.createElement('script');
            script.src = 'https://viacep.com.br/ws/'+ cep + '/json/?callback=meu_callback';
            document.body.appendChild(script);

        } 
        else {
            limpa_formulário_cep();
            alert("Formato de CEP inválido.");
        }
    } 
    else {
        limpa_formulário_cep();
    }
};

function enableAndSubmitForm() {
    document.getElementById("bairro").disabled = false;
    document.getElementById("cidade").disabled = false;
    document.getElementById("uf").disabled = false;
    document.getElementById("cadastroForm").submit();
}
