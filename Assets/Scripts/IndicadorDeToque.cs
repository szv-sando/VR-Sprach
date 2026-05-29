using UnityEngine;
using UnityEngine.EventSystems;
using System.Collections.Generic;
using UnityEngine.InputSystem;

public class IndicadorDeToque : MonoBehaviour
{
    void Update()
    {
        // Verifica se o mouse existe e se o botão esquerdo foi clicado neste exato frame
        if (Mouse.current != null && Mouse.current.leftButton.wasPressedThisFrame)
        {
            // Cria um "raio" virtual a partir da posição exata do mouse na tela
            PointerEventData pointerData = new PointerEventData(EventSystem.current);
            pointerData.position = Mouse.current.position.ReadValue();

            // Dispara o raio contra o Canvas e anota tudo que ele atravessar
            List<RaycastResult> results = new List<RaycastResult>();
            EventSystem.current.RaycastAll(pointerData, results);

            // Imprime no Console o resultado
            if (results.Count > 0)
            {
                Debug.Log("🎯 Toque detectado! O objeto que recebeu o clique foi: " + results[0].gameObject.name);
            }
            else
            {
                Debug.Log("⚠️ Toque no vazio! Nenhum objeto de UI foi atingido.");
            }
        }
    }
}