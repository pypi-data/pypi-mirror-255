export default {
  meta: {
    inMenu: true,
    titleKey: "evalu.menu_title",
    icon: "mdi-forum-outline",
    permission: "evalu.view_menu_rule",
  },
  props: {
    byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
  },
  children: [
    {
      path: "parts/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.evaluationParts",
      meta: {
        inMenu: true,
        titleKey: "evalu.parts.menu_title",
        icon: "mdi-format-list-bulleted-type",
        permission: "evalu.view_evaluation_parts",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "parts/create/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.createEvaluationPart",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "parts/:pk/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.editEvaluationPart",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "parts/:pk/delete/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.deleteEvaluationPart",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "phases/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.evaluationPhases",
      meta: {
        inMenu: true,
        titleKey: "evalu.phases.menu_title",
        icon: "mdi-calendar-range-outline",
        permission: "evalu.view_evaluation_phases",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "phases/create/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.createEvaluationPhase",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "phases/:pk/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.evaluationPhase",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "phases/:pk/edit/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.editEvaluationPhase",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "phases/:pk/delete/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.deleteEvaluationPhase",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "phases/:pk/deletion/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.deleteDataFromPhase",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "evaluations/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.evaluationPhasesOverview",
      meta: {
        inMenu: true,
        titleKey: "evalu.evaluation.all_menu_title",
        icon: "mdi-format-list-checks",
        permission: "evalu.view_evaluationphases_overview_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "evaluations/:pk/register/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.registerForEvaluation",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "evaluations/registrations/:pk/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.evaluationRegistration",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "evaluations/registrations/:pk/manage/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.manageEvaluationProcess",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "evaluations/groups/:pk/start/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.startEvaluationForGroup",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "evaluations/groups/:pk/stop/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.stopEvaluationForGroup",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "evaluations/groups/:pk/custom_items/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.editCustomEvaluationItems",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "evaluations/registrations/:pk/finish/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.finishEvaluation",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "evaluations/registrations/:pk/results/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.evaluationResults",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "evaluations/registrations/:pk/results/pdf/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.evaluationResultsAsPdf",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "evaluations/evaluate/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.evaluationsAsParticipant",
      meta: {
        inMenu: true,
        titleKey: "evalu.evaluation.my_menu_title",
        icon: "mdi-comment-quote-outline",
        permission: "evalu.view_evaluations_as_participant_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "evaluations/evaluate/:pk/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "evalu.evaluatePerson",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
  ],
};
