import { useApi } from "~/composables/use-api";

export type QuestionType = "ChoixMultiple" | "VraiOuFaux" | "QuestionOuverte" | "ListeOuverte";

export type Question = {
  numero: number;
  question: string;
  type: QuestionType;
  options?: string[];
  correction?: string | string[];
};

export type Answer = {
  numero: number;
  question: string;
  type: QuestionType;
  options?: string[];
  user_answer: string;
  correct_answer?: string | string[];
  is_correct?: boolean | string;
};

export type QuestionnaireResult = {
  score: string;
  score_percentage: number;
  completed_at: string;
  questions_data: Answer[];
};

export type TaskStatus = {
  task_id: string;
  status: string;
  result?: any;
  error?: string;
};

export function useQuestionnaire() {
  const api = useApi();
  const questions = useState<Question[] | null>("questionnaire_questions", () => null);
  const currentQuestionIndex = useState<number>("questionnaire_current_index", () => 0);
  const answers = useState<Record<string, string>>("questionnaire_answers", () => ({}));
  const quizCompleted = useState<boolean>("questionnaire_completed", () => false);
  const evaluationResult = useState<QuestionnaireResult | null>("questionnaire_result", () => null);
  const questionTaskId = useState<string | null>("questionnaire_task_id", () => null);
  const analysisTaskId = useState<string | null>("questionnaire_analysis_task_id", () => null);
  const taskCheckAttempts = useState<number>("questionnaire_attempts", () => 0);

  // Générer le questionnaire
  const generateQuestionnaire = async () => {
    try {
      const data = await api.questionnaire.generateQuestions();

      if (data?.task_id) {
        questionTaskId.value = data.task_id;
        taskCheckAttempts.value = 0;
        return data.task_id;
      }

      throw new Error("Aucun task_id reçu");
    }
    catch (e: any) {
      console.error("Erreur generateQuestionnaire:", e);
      throw e;
    }
  };

  // Vérifier le statut de la tâche
  const checkTaskStatus = async (taskId: string): Promise<TaskStatus | null> => {
    try {
      const data = await api.questionnaire.getQuestionResult(taskId);
      return data as TaskStatus;
    }
    catch (e: any) {
      console.error("Erreur checkTaskStatus:", e);
      return null;
    }
  };

  // Parser le résultat des questions
  const parseQuestionsPayload = (resultData: any): Question[] | null => {
    try {
      if (!resultData || typeof resultData !== "object") {
        return null;
      }

      // Priorité 1: Si 'json' existe et est déjà une liste
      if (resultData.json && Array.isArray(resultData.json)) {
        return resultData.json;
      }

      // Priorité 2: Si 'json' est une string, tenter de parser
      if (resultData.json && typeof resultData.json === "string") {
        try {
          const parsed = JSON.parse(resultData.json);
          if (Array.isArray(parsed)) {
            return parsed;
          }
        }
        catch (e) {
          console.error("Erreur parsing json string:", e);
        }
      }

      // Priorité 3: Si 'question' contient le JSON
      if (resultData.question && typeof resultData.question === "string") {
        try {
          const parsed = JSON.parse(resultData.question);
          if (Array.isArray(parsed)) {
            return parsed;
          }
        }
        catch (e) {
          console.error("Erreur parsing question string:", e);
        }
      }

      // Priorité 4: Chercher toute clé contenant une liste de questions
      for (const key in resultData) {
        const value = resultData[key];
        if (Array.isArray(value) && value.length > 0) {
          if (value.every(item => typeof item === "object" && item !== null && "question" in item)) {
            return value;
          }
        }
      }

      return null;
    }
    catch (e) {
      console.error("Erreur parseQuestionsPayload:", e);
      return null;
    }
  };

  // Générer les résultats d'évaluation
  const generateEvaluationResult = (): QuestionnaireResult => {
    const questionsList = (questions.value || []).filter((q): q is Question => Boolean(q));
    const evaluationData: Answer[] = [];

    for (let i = 0; i < questionsList.length; i++) {
      const q = questionsList[i]!; // ! car on a filtré les undefined
      const qKey = `q_${i}`;
      const userAnswer = answers.value[qKey] || "";

      // Déterminer si la réponse est correcte
      let isCorrect: boolean | string = false;

      // Si pas de réponse, marquer comme "Non répondu"
      if (!userAnswer || userAnswer.trim() === "") {
        isCorrect = "Non répondu";
      }
      else if (q.type === "QuestionOuverte" || q.type === "ListeOuverte") {
        isCorrect = "Non évalué (requiert une analyse humaine)";
      }
      else {
        const correctAnswer = q.correction || "";
        if (Array.isArray(correctAnswer)) {
          isCorrect = correctAnswer.includes(userAnswer);
        }
        else {
          // Vérifier si la réponse commence par la lettre de la correction (A, B, C, D)
          const firstLetter = correctAnswer.split(" ")[0];
          isCorrect = !!userAnswer && userAnswer.trim().startsWith(firstLetter);
        }
      }

      evaluationData.push({
        numero: q.numero || i + 1,
        question: q.question || "",
        type: q.type || "ChoixMultiple",
        options: q.options || [],
        user_answer: userAnswer,
        correct_answer: q.correction,
        is_correct: isCorrect,
      });
    }

    // Calculer le score
    const score = evaluationData.filter(item => item.is_correct === true).length;
    // Exclure les questions non évaluables ET non répondues du calcul du total
    const total = evaluationData.filter(item =>
      item.is_correct !== "Non évalué (requiert une analyse humaine)"
      && item.is_correct !== "Non répondu",
    ).length;

    return {
      score: `${score}/${total}`,
      score_percentage: total > 0 ? Math.round((score / total) * 100 * 100) / 100 : 0,
      completed_at: new Date().toISOString(),
      questions_data: evaluationData,
    };
  };

  // Soumettre le questionnaire
  const submitQuestionnaire = async () => {
    const result = generateEvaluationResult();
    evaluationResult.value = result;
    quizCompleted.value = true;

    console.warn("📤 Soumission du questionnaire avec résultats:", {
      score: result.score,
      score_percentage: result.score_percentage,
      questions_answered: result.questions_data.filter(q => q.is_correct !== "Non répondu").length,
      total_questions: result.questions_data.length,
    });

    // Envoyer les résultats au backend pour analyse
    try {
      const response = await api.questionnaire.analyzeQuiz(result);

      console.warn("📥 Réponse du backend:", response);

      if (response?.task_id) {
        console.warn(`✅ Task d'analyse créé: ${response.task_id}`);
        // Retourner le task_id de l'analyse pour pouvoir vérifier son statut
        return { result, analysisTaskId: response.task_id };
      }

      console.error("❌ Aucun task_id retourné par le backend");
      throw new Error("Le backend n'a pas retourné de task_id pour l'analyse");
    }
    catch (e: any) {
      console.error("❌ Erreur submitQuestionnaire:", e);
      throw e;
    }
  };

  // Vérifier le statut de la tâche d'analyse
  const checkAnalysisStatus = async (taskId: string): Promise<any> => {
    try {
      const data = await api.questionnaire.getAnalysisResult(taskId);
      return data;
    }
    catch (e: any) {
      console.error("Erreur checkAnalysisStatus:", e);
      return null;
    }
  };

  // Réinitialiser le questionnaire
  const resetQuestionnaire = () => {
    questions.value = null;
    currentQuestionIndex.value = 0;
    answers.value = {};
    quizCompleted.value = false;
    evaluationResult.value = null;
    questionTaskId.value = null;
    analysisTaskId.value = null;
    taskCheckAttempts.value = 0;
  };

  return {
    questions,
    currentQuestionIndex,
    answers,
    quizCompleted,
    evaluationResult,
    questionTaskId,
    analysisTaskId,
    taskCheckAttempts,
    generateQuestionnaire,
    checkTaskStatus,
    checkAnalysisStatus,
    parseQuestionsPayload,
    generateEvaluationResult,
    submitQuestionnaire,
    resetQuestionnaire,
  };
}
