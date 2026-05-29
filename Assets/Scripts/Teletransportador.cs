using UnityEngine;
using UnityEngine.SceneManagement; // A biblioteca mágica que permite viajar entre as fases

public class Teletransportador : MonoBehaviour
{
    [Header("Configuração do Portal")]
    [Tooltip("Digite o nome EXATO da cena para onde este domo vai levar")]
    public string nomeDaCenaDestino;

    // Essa função é ativada no exato milissegundo em que um corpo físico atravessa o domo
    private void OnTriggerEnter(Collider outroObjeto)
    {
        // Verifica se quem encostou foi o jogador (evita que outros objetos ativem o portal)
        if (outroObjeto.CompareTag("Player"))
        {
            Debug.Log("Iniciando viagem dimensional para: " + nomeDaCenaDestino);
            SceneManager.LoadScene(nomeDaCenaDestino);
        }
    }
}