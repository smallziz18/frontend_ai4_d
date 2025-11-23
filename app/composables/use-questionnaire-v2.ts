// Composable pour le système de questionnaire V2 (LangGraph Multi-Agents)
import { useApi } from "~/composables/use-api";

export type QuestionV2 = {
  numero: number;
  question: string;
  type: "ChoixMultiple" | "VraiOuFaux" | "QuestionOuverte" | "ListeOuverte";
  options?: string[];
  correction: string;
};

export type ResponseV2 = {
  numero: number;
  reponse: string;
  type: string;
};

export type QuestionnaireSessionV2 = {
  session_id: string;
  questions: QuestionV2[];
  profiler_analysis: {
    niveau_estime: number;
    style_apprentissage: string;
    motivation: string;
  };
  timestamp: string;
};

export type AnalysisResultV2 = {
  session_id: string;
  niveau_final: number;
  evaluation: {
    score_total: number;
    score_percentage: number;
    details_par_question: any[];
  };
  parcours_apprentissage: {
    titre: string;
    duree_estimee: string;
    quetes_principales: Array<{
      id: string;
      titre: string;
      description: string;
      objectifs: string[];
      ressources: any[];
      exercices: string[];
      xp: number;
      badge: string;
    }>;
    boss_fights: Array<{
      id: string;
      titre: string;
      description: string;
      prerequis: string[];
      xp: number;
      badge: string;
    }>;
  };
  tutorials: any[];
  gamification: {
    badges_earned: string[];
    xp_gained: number;
    level_up: boolean;
  };
  recommendations: string[];
  timestamp: string;
};

export function useQuestionnaireV2() {
  const api = useApi();

  // État du questionnaire
  const session = useState<QuestionnaireSessionV2 | null>("questionnaire_v2_session", () => null);
  const currentQuestionIndex = useState<number>("questionnaire_v2_current_index", () => 0);
  const answers = useState<Record<string, string>>("questionnaire_v2_answers", () => ({}));
  const analysisResult = useState<AnalysisResultV2 | null>("questionnaire_v2_analysis", () => null);
  const loading = useState<boolean>("questionnaire_v2_loading", () => false);
  const quizCompleted = useState<boolean>("questionnaire_v2_completed", () => false);

  // Question actuelle
  const currentQuestion = computed(() => {
    if (!session.value || !session.value.questions)
      return null;
    return session.value.questions[currentQuestionIndex.value];
  });

  // Progression
  const progress = computed(() => {
    if (!session.value || !session.value.questions)
      return 0;
    return ((currentQuestionIndex.value + 1) / session.value.questions.length) * 100;
  });

  // Nombre de réponses
  const answeredCount = computed(() => Object.keys(answers.value).length);
  const totalQuestions = computed(() => session.value?.questions.length || 0);

  // Générer un nouveau questionnaire
  const generateQuestionnaire = async () => {
    try {
      loading.value = true;
      const data = await api.questionnaireV2.generateQuestions();

      session.value = data;
      currentQuestionIndex.value = 0;
      answers.value = {};
      quizCompleted.value = false;
      analysisResult.value = null;

      return data;
    }
    catch (e: any) {
      console.error("Erreur lors de la génération du questionnaire V2:", e);
      throw new Error(e.message || "Impossible de générer le questionnaire");
    }
    finally {
      loading.value = false;
    }
  };

  // Soumettre les réponses
  const submitResponses = async () => {
    if (!session.value) {
      throw new Error("Aucune session active");
    }

    try {
      loading.value = true;

      // Construire le tableau de réponses
      const responses: ResponseV2[] = session.value.questions.map((q) => {
        const questionKey = `q_${q.numero - 1}`;
        return {
          numero: q.numero,
          reponse: answers.value[questionKey] || "",
          type: q.type,
        };
      });

      const result = await api.questionnaireV2.submitResponses(
        session.value.session_id,
        responses,
      );

      analysisResult.value = result;
      quizCompleted.value = true;

      return result;
    }
    catch (e: any) {
      console.error("Erreur lors de la soumission des réponses V2:", e);
      throw new Error(e.message || "Impossible de soumettre les réponses");
    }
    finally {
      loading.value = false;
    }
  };

  // Récupérer le parcours d'apprentissage
  const getLearningPath = async () => {
    try {
      return await api.questionnaireV2.getLearningPath();
    }
    catch (e: any) {
      console.error("Erreur lors de la récupération du parcours:", e);
      throw new Error(e.message || "Impossible de récupérer le parcours");
    }
  };

  // Récupérer l'état du workflow (debugging)
  const getWorkflowState = async (sessionId: string) => {
    try {
      return await api.questionnaireV2.getWorkflowState(sessionId);
    }
    catch (e: any) {
      console.error("Erreur lors de la récupération de l'état du workflow:", e);
      return null;
    }
  };

  // Navigation
  const nextQuestion = () => {
    if (session.value && currentQuestionIndex.value < session.value.questions.length - 1) {
      currentQuestionIndex.value++;
    }
  };

  const previousQuestion = () => {
    if (currentQuestionIndex.value > 0) {
      currentQuestionIndex.value--;
    }
  };

  const goToQuestion = (index: number) => {
    if (session.value && index >= 0 && index < session.value.questions.length) {
      currentQuestionIndex.value = index;
    }
  };

  // Réponse à une question
  const setAnswer = (questionKey: string, answer: string) => {
    answers.value[questionKey] = answer;
  };

  // Réinitialiser le questionnaire
  const reset = () => {
    session.value = null;
    currentQuestionIndex.value = 0;
    answers.value = {};
    analysisResult.value = null;
    loading.value = false;
    quizCompleted.value = false;
  };

  // Vérifier si toutes les questions ont une réponse
  const allQuestionsAnswered = computed(() => {
    if (!session.value)
      return false;
    return session.value.questions.every((q) => {
      const questionKey = `q_${q.numero - 1}`;
      return answers.value[questionKey] && answers.value[questionKey].trim() !== "";
    });
  });

  return {
    // État
    session,
    currentQuestionIndex,
    answers,
    analysisResult,
    loading,
    quizCompleted,

    // Computed
    currentQuestion,
    progress,
    answeredCount,
    totalQuestions,
    allQuestionsAnswered,

    // Actions
    generateQuestionnaire,
    submitResponses,
    getLearningPath,
    getWorkflowState,
    nextQuestion,
    previousQuestion,
    goToQuestion,
    setAnswer,
    reset,
  };
}
