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
  const questions = useState<Question[] | null>("questionnaire_questions", () => null);
  const currentQuestionIndex = useState<number>("questionnaire_current_index", () => 0);
  const answers = useState<Record<string, string>>("questionnaire_answers", () => ({}));
  const quizCompleted = useState<boolean>("questionnaire_completed", () => false);
  const evaluationResult = useState<QuestionnaireResult | null>("questionnaire_result", () => null);
  const questionTaskId = useState<string | null>("questionnaire_task_id", () => null);
  const taskCheckAttempts = useState<number>("questionnaire_attempts", () => 0);

  // Générer le questionnaire
  const generateQuestionnaire = async () => {
    try {
      const accessToken = useCookie("access_token").value;

      const data = await $fetch<{ task_id: string }>(
        "http://127.0.0.1:8000/api/profile/v1/question",
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        },
      );

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
      const accessToken = useCookie("access_token").value;

      const data = await $fetch<TaskStatus>(
        `http://127.0.0.1:8000/api/profile/v1/question_result/${taskId}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        },
      );

      return data;
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
    const questionsList = questions.value || [];
    const evaluationData: Answer[] = [];

    for (let i = 0; i < questionsList.length; i++) {
      const q = questionsList[i];
      const qKey = `q_${i}`;
      const userAnswer = answers.value[qKey] || "";

      // Déterminer si la réponse est correcte
      let isCorrect: boolean | string = false;
      if (q.type === "QuestionOuverte" || q.type === "ListeOuverte") {
        isCorrect = "Non évalué (requiert une analyse humaine)";
      }
      else {
        const correctAnswer = q.correction || "";
        if (Array.isArray(correctAnswer)) {
          isCorrect = correctAnswer.includes(userAnswer);
        }
        else if (typeof correctAnswer === "string") {
          // Vérifier si la réponse commence par la lettre de la correction (A, B, C, D)
          isCorrect = userAnswer && userAnswer.trim().startsWith(correctAnswer.split(" ")[0]);
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
    const total = evaluationData.filter(item => item.is_correct !== "Non évalué (requiert une analyse humaine)").length;

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

    // Marquer le questionnaire comme terminé
    const hasCompletedQuestionnaire = useCookie("questionnaire_completed", {
      maxAge: 60 * 60 * 24 * 365, // 1 an
    });
    hasCompletedQuestionnaire.value = true as any;

    // Envoyer les résultats au backend
    try {
      const accessToken = useCookie("access_token").value;

      await $fetch(
        "http://127.0.0.1:8000/api/profile/v1/analyze_quiz",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
          body: result,
        },
      );
    }
    catch (e: any) {
      console.error("Erreur submitQuestionnaire:", e);
    }

    return result;
  };

  // Réinitialiser le questionnaire
  const resetQuestionnaire = () => {
    questions.value = null;
    currentQuestionIndex.value = 0;
    answers.value = {};
    quizCompleted.value = false;
    evaluationResult.value = null;
    questionTaskId.value = null;
    taskCheckAttempts.value = 0;
  };

  return {
    questions,
    currentQuestionIndex,
    answers,
    quizCompleted,
    evaluationResult,
    questionTaskId,
    taskCheckAttempts,
    generateQuestionnaire,
    checkTaskStatus,
    parseQuestionsPayload,
    generateEvaluationResult,
    submitQuestionnaire,
    resetQuestionnaire,
  };
}
