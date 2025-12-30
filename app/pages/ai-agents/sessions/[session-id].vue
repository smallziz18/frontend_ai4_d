<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import { useApi } from "~/composables/use-api";

// Support different param names produced by backend / router
const route = useRoute();
const sessionId = computed(() => {
  return (
    (route.params["session-id"] as string)
    || (route.params.session_id as string)
    || (route.params.id as string)
    || ""
  );
});

const api = useApi();

const sessionState = ref<any>(null);
const history = ref<any[]>([]);
const summary = ref<any>(null);
const loading = ref(false);
const error = ref("");
const newMessage = ref("");

async function loadSession() {
  const id = sessionId.value;
  if (!id) {
    error.value = "Identifiant de session manquant.";
    return;
  }

  loading.value = true;
  error.value = "";
  try {
    sessionState.value = await api.ai.getSessionState(id);

    // Normalize history response from multiple backend shapes
    const histRes = await api.ai.getSessionHistory(id);
    let normalized: any[] = [];

    if (Array.isArray(histRes)) {
      normalized = histRes;
    }
    else if (histRes && Array.isArray((histRes as any).conversation)) {
      normalized = (histRes as any).conversation;
    }
    else if (histRes && Array.isArray((histRes as any).conversations)) {
      normalized = (histRes as any).conversations;
    }
    else if (histRes && Array.isArray((histRes as any).history)) {
      normalized = (histRes as any).history;
    }
    else if (histRes && (histRes as any).conversation && Array.isArray((histRes as any).conversation.messages)) {
      normalized = (histRes as any).conversation.messages;
    }
    else if (histRes && typeof histRes === "object") {
      // try to extract message-like arrays
      const possible = histRes as any;
      const keys = ["messages", "items", "events"];
      for (const k of keys) {
        if (Array.isArray(possible[k])) {
          normalized = possible[k];
          break;
        }
      }
    }

    history.value = normalized;

    const summ = await api.ai.getSessionSummary(id);
    // summary may be an object or { summary: ... }
    summary.value = (summ && (summ as any).summary) ? (summ as any).summary : summ;
  }
  catch (e: any) {
    error.value = e?.message ?? "Erreur lors du chargement de la session";
  }
  finally {
    loading.value = false;
  }
}

async function sendMessage() {
  if (!newMessage.value) {
    return;
  }

  loading.value = true;
  try {
    // use computed sessionId value
    await api.ai.addManualMessage(sessionId.value, { content: newMessage.value });
    newMessage.value = "";
    await loadSession();
  }
  catch (e: any) {
    error.value = e?.message ?? "Erreur en envoyant le message";
  }
  finally {
    loading.value = false;
  }
}

// Auto-load when route param becomes available or changes
onMounted(() => {
  if (sessionId.value)
    loadSession();
});

watch(sessionId, (val) => {
  if (val)
    loadSession();
});
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">
        Session AI - {{ sessionId || '—' }}
      </h1>
      <div class="flex gap-2">
        <NuxtLink to="/ai-agents" class="btn btn-ghost">
          Retour
        </NuxtLink>
        <button class="btn btn-outline" @click="loadSession">
          Rafraîchir
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-error mb-4">
      {{ error }}
    </div>

    <div v-if="loading" class="mb-4">
      <div class="alert alert-info">
        Chargement…
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="col-span-2 space-y-4">
        <div class="card bg-base-100 shadow">
          <div class="card-body">
            <h3 class="card-title">
              État du workflow
            </h3>
            <pre class="text-sm overflow-auto max-h-60">{{ sessionState ? JSON.stringify(sessionState, null, 2) : '—' }}</pre>
          </div>
        </div>

        <div class="card bg-base-100 shadow">
          <div class="card-body">
            <h3 class="card-title">
              Historique
            </h3>
            <div v-if="history.length === 0" class="text-sm text-gray-500">
              Aucun historique
            </div>
            <ul class="space-y-2 mt-2">
              <li
                v-for="(h, i) in history"
                :key="i"
                class="p-2 bg-base-200 rounded"
              >
                <template v-if="h && (h.role || h.content)">
                  <div class="flex justify-between items-start">
                    <div>
                      <div class="font-semibold">
                        {{ h.role ?? 'message' }}
                      </div>
                      <div class="whitespace-pre-wrap">
                        {{ typeof h.content === 'string' ? h.content : JSON.stringify(h.content ?? h, null, 2) }}
                      </div>
                    </div>
                    <div class="text-xs text-gray-500 ml-2">
                      {{ h.timestamp ?? h.created_at ?? '' }}
                    </div>
                  </div>
                </template>
                <template v-else>
                  <pre class="text-sm">{{ typeof h === 'string' ? h : JSON.stringify(h, null, 2) }}</pre>
                </template>
              </li>
            </ul>
          </div>
        </div>

        <div class="card bg-base-100 shadow">
          <div class="card-body">
            <h3 class="card-title">
              Résumé
            </h3>
            <pre class="text-sm overflow-auto max-h-40">{{ summary ? JSON.stringify(summary, null, 2) : '—' }}</pre>
          </div>
        </div>

        <div class="card bg-base-100 shadow">
          <div class="card-body">
            <h3 class="card-title">
              Envoyer un message manuel
            </h3>
            <textarea
              v-model="newMessage"
              class="textarea textarea-bordered w-full h-24"
              placeholder="Votre message"
            />
            <div class="mt-2 text-right">
              <button
                class="btn btn-primary"
                :disabled="loading"
                @click="sendMessage"
              >
                Envoyer
              </button>
            </div>
          </div>
        </div>
      </div>

      <div>
        <div class="card bg-base-100 shadow p-4">
          <h3 class="text-lg font-semibold mb-2">
            Détails rapides
          </h3>
          <p><strong>Statut:</strong> {{ sessionState?.status ?? 'unknown' }}</p>
          <p><strong>Agents impliqués:</strong> {{ sessionState?.agents ?? '—' }}</p>
          <p><strong>Crée le:</strong> {{ sessionState?.created_at ?? sessionState?.createdAt ?? '—' }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
