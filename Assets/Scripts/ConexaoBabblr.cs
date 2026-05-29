using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using TMPro; // Para TextMeshPro
using UnityEngine.UI; // Para o Button

public class ConexaoBabblr : MonoBehaviour
{
    [Header("Interface (UI)")]
    public TMP_Text textoVR; // Onde aparece a pergunta
    public TMP_InputField caixaDeResposta; // Onde o jogador digita
    public TMP_Text textoFeedback; // Onde aparece se acertou/errou
    public Button botaoEnviarUI; // O botão em si
    public TMP_Text textoBotaoLabel; // O texto dentro do botão (ENVIAR / AVANÇAR)

    [Header("Controles do Jogador")]
    public StarterAssets.StarterAssetsInputs inputsDoJogador; // Puxa do PlayerCapsule

    [Header("Configurações do Servidor")]
    private string urlGerar = "http://127.0.0.1:5000/gerar-exercicio";
    private string urlAvaliar = "http://127.0.0.1:5000/avaliar-resposta";

    private bool modoAvancar = false; // Controla se o botão está no modo Enviar ou Avançar

    void Start()
    {
        // Trava o mouse no centro exato da tela e esconde a setinha do Windows
        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;

        PrepareNovoExercicio();
    }

void Update()
    {
        // 1. O botão ESC para soltar o mouse
        if (UnityEngine.InputSystem.Keyboard.current != null && UnityEngine.InputSystem.Keyboard.current.escapeKey.wasPressedThisFrame)
        {
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
        }

        // 2. A trava definitiva do boneco
        if (caixaDeResposta != null && inputsDoJogador != null)
        {
            // Pega o "cérebro" do Novo Sistema de Inputs que está no seu boneco
            var cerebroDoBoneco = inputsDoJogador.GetComponent<UnityEngine.InputSystem.PlayerInput>();

            if (cerebroDoBoneco != null)
            {
                if (caixaDeResposta.isFocused)
                {
                    // Se estiver digitando, desliga os controles do boneco (ele não anda, não pula e não vira a câmera)
                    cerebroDoBoneco.enabled = false; 
                }
                else
                {
                    // Se clicar fora da caixa, religa os controles
                    cerebroDoBoneco.enabled = true; 
                }
            }
        }
    }

    // Função conectada ao Clique do Botão
    public void BotaoEnviarPressionado()
    {
        // SE ESTIVER NO MODO "AVANÇAR", PEGA NOVA PERGUNTA
        if (modoAvancar)
        {
            PrepareNovoExercicio();
            return;
        }

        // SE ESTIVER NO MODO "ENVIAR", AVALIA A RESPOSTA
        string textoDoAluno = caixaDeResposta.text;
        if (string.IsNullOrWhiteSpace(textoDoAluno)) return;

        // Feedback Visual de Carregamento
        if (textoFeedback != null)
        {
            textoFeedback.color = Color.yellow;
            textoFeedback.text = "Avaliando resposta... O professor está lendo!";
        }

        if (botaoEnviarUI != null) botaoEnviarUI.interactable = false;

        StartCoroutine(EnviarRespostaParaAvaliacao(textoDoAluno));
    }

    // Limpa a tela e pede um exercício novo
    private void PrepareNovoExercicio()
    {
        modoAvancar = false;
        
        if (textoBotaoLabel != null) textoBotaoLabel.text = "ENVIAR";
        if (caixaDeResposta != null) caixaDeResposta.text = "";
        if (textoFeedback != null) textoFeedback.text = "Aguardando o professor criar o exercício...";
        if (textoFeedback != null) textoFeedback.color = Color.white;

        StartCoroutine(GerarExercicio()); // Chama a rotina de buscar no Python
    }

    // ROTINA 1: Pede a pergunta para a IA
    IEnumerator GerarExercicio()
    {
        // Cria o pacote JSON pedindo nível iniciante
        string json = "{\"nivel\":\"iniciante\"}";

        UnityWebRequest request = new UnityWebRequest(urlGerar, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(json);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();

if (request.result == UnityWebRequest.Result.Success)
        {
            // Nosso Soro da Verdade #1
            Debug.Log("O que chegou do Python: " + request.downloadHandler.text); 
            
            // A variável 'res' criada UMA ÚNICA VEZ
            RespostaExercicio res = JsonUtility.FromJson<RespostaExercicio>(request.downloadHandler.text);
            
            // Nosso Soro da Verdade #2
            Debug.Log("O que o Unity entendeu da frase: " + res.texto_exercicio); 
            
            if (textoVR != null) textoVR.text = res.texto_exercicio;
            if (textoFeedback != null) textoFeedback.text = ""; 
        }
        else
        {
            if (textoFeedback != null)
            {
                textoFeedback.color = Color.red;
                textoFeedback.text = "Erro ao conectar com o Cérebro da IA.";
            }
        }

        if (request.result == UnityWebRequest.Result.Success)
        {
            // O SORO DA VERDADE: Vai imprimir no Console exatamente o que o Python mandou
            Debug.Log("O que chegou do Python: " + request.downloadHandler.text); 
            
            RespostaExercicio res = JsonUtility.FromJson<RespostaExercicio>(request.downloadHandler.text);
            if (textoVR != null) textoVR.text = res.texto_exercicio;
            if (textoFeedback != null) textoFeedback.text = ""; 
        }
    }

    // ROTINA 2: Envia a resposta do aluno para a IA corrigir
    IEnumerator EnviarRespostaParaAvaliacao(string resposta)
    {
        // Transforma a resposta do aluno em JSON (precisa escapar as aspas para não quebrar)
        string json = "{\"resposta\":\"" + resposta.Replace("\"", "\\\"") + "\"}";

        UnityWebRequest request = new UnityWebRequest(urlAvaliar, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(json);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            RespostaAvaliacao res = JsonUtility.FromJson<RespostaAvaliacao>(request.downloadHandler.text);
            
            if (textoFeedback != null)
            {
                textoFeedback.color = res.acertou ? Color.green : Color.red;
                textoFeedback.text = "Resultado: " + (res.acertou ? "ACERTOU!" : "ERROU!") + "\n" + res.feedback;
            }

            // Transforma o botão em AVANÇAR
            if (botaoEnviarUI != null)
            {
                botaoEnviarUI.interactable = true;
                modoAvancar = true;
                if (textoBotaoLabel != null) textoBotaoLabel.text = "AVANÇAR";
            }
        }
        else
        {
            if (textoFeedback != null)
            {
                textoFeedback.color = Color.red;
                textoFeedback.text = "Erro ao enviar avaliação.";
            }
            if (botaoEnviarUI != null) botaoEnviarUI.interactable = true; // Destrava se der erro
        }
    }

    // CLASSES PARA LER O JSON QUE VEM DO PYTHON
    [System.Serializable]
    public class RespostaExercicio
    {
        public bool sucesso;
        public string texto_exercicio;
    }

    [System.Serializable]
    public class RespostaAvaliacao
    {
        public bool sucesso;
        public bool acertou;
        public string feedback;
    }
}