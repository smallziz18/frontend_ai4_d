<script setup lang="ts">
</script>

<template>
  <main>
    <div class="hero bg-base-200 mt-5">
      <div class="hero-content flex-col lg:flex-row-reverse">
        <img
          src="https://img.daisyui.com/images/stock/photo-1635805737707-575885ab0820.webp"
          class="max-w-sm rounded-lg shadow-2xl"
          alt="null"
        >
        <div>
          <h1 class="text-5xl font-bold">
            Unlock Your Potential with AI-Powered Learning !
          </h1>
          <p class="py-6">
            Personalized education and profile management to help you achieve your goals.
          </p>
        </div>
      </div>
    </div>
    <div>
      <div>
        <h1 class="text-5xl font-bold text-center mt-10">
          Our Courses
        </h1>
        <p class="py-6 text-center">
          Explore our wide range of courses designed to help you master new skills and advance your career.
        </p>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
        <div class="card bg-primary text-primary-content h-full flex flex-col">
          <div class="card-body flex-1 flex flex-col items-center">
            <Icon name="tabler:robot-face" size="36" />
            <h2 class="card-title text-center">
              AI-Powered Tutors !
            </h2>
            <p class="text-center flex-1">
              Get instant support and guidance from our advanced AI tutors, available 24/7.
            </p>
          </div>
        </div>
        <div class="card bg-primary text-primary-content h-full flex flex-col">
          <div class="card-body flex-1 flex flex-col items-center">
            <Icon name="tabler:user-filled" size="36" />
            <h2 class="card-title text-center">
              Profile Management!
            </h2>
            <p class="text-center flex-1">
              Showcase your skills and achievements with a dynamic, AI-enhanced profile.
            </p>
          </div>
        </div>
        <div class="card bg-primary text-primary-content h-full flex flex-col">
          <div class="card-body flex-1 flex flex-col items-center">
            <Icon name="tabler:book-filled" size="36" />
            <h2 class="card-title text-center">
              Personalized Learning Paths!
            </h2>
            <p class="text-center flex-1">
              Tailored learning paths that adapt to your unique needs and goals.
            </p>
          </div>
        </div>
      </div>
    </div>
    <div id="testimonials" class="px-4 md:px-10 py-16 md:py-24">
      <h2 class="font-heading text-3xl font-bold leading-tight tracking-tight text-center mb-12 text-text-light dark:text-text-dark">
        What Our Users Are Saying
      </h2>
      <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div class="flex flex-col gap-4 rounded-xl p-6 bg-white dark:bg-gray-800 shadow-md">
          <div class="flex items-center gap-4">
            <div
              class="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-12"
              data-alt="Portrait of Jane Doe"
              style="background-image: url(&quot;https://lh3.googleusercontent.com/aida-public/AB6AXuAm4IF3rbW6fC5fyb1ujf9EB3R4Iqg8KSShxve3QJfPCTIQGpxr0_ROnPbw01SBpAZ9dPPXMMsxZVSrCfL9yl9PGsRoZQnP0SQbwC57vXERSUT2-6Y95AvEvHtbrtJq-V77Jn_JtQEDtRjr89jKYJdF0-h22zpQI9GRDxVAIws0ckV2hlwK6p-mtbWjYbLXeTUlT2yb9hWqbZLxDFx-ZtWG-PWXNnHm2rH6l0VqXEGUGk0ih2KSMDUwIfvzqyQ9qsKXv6PA1Ya9CQ&quot;);"
            />
            <div>
              <p class="text-base font-medium text-text-light dark:text-text-dark">
                Jane Doe
              </p>
              <div class="flex gap-0.5 text-accent">
                <span class="material-symbols-outlined !text-base" style="font-variation-settings: 'FILL' 1;">star</span>
                <span class="material-symbols-outlined !text-base" style="font-variation-settings: 'FILL' 1;">star</span>
                <span class="material-symbols-outlined !text-base" style="font-variation-settings: 'FILL' 1;">star</span>
                <span class="material-symbols-outlined !text-base" style="font-variation-settings: 'FILL' 1;">star</span>
                <span class="material-symbols-outlined !text-base" style="font-variation-settings: 'FILL' 1;">star</span>
              </div>
            </div>
          </div>
          <p class="text-base font-normal leading-normal text-gray-600 dark:text-gray-400">
            "The personalized learning paths have been a game-changer for my career. I've learned more in three months than I did in a year of traditional courses."
          </p>
        </div>
        <div class="flex flex-col gap-4 rounded-xl p-6 bg-white dark:bg-gray-800 shadow-md">
          <div class="flex items-center gap-4">
            <div
              class="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-12"
              data-alt="Portrait of John Smith"
              style="background-image: url(&quot;https://lh3.googleusercontent.com/aida-public/AB6AXuCj5l1g0tLvYKfCjb2QCmswbmH_s0nPEzh80_GOO4oObcJdAtXd-t-dQFms9k2OpvyAE2MQaIR_VLkJbV74_pmxc7ePgpH3oaBib7taNc8KE8VdLgHXG0Mm9nONHzLP_kirOLqNVKCorjJJ9xKIc6emNqSc0v0TGSLYjGdIcFuDShFzngdMuUfxvVZtWkNmx2NWeccRTargWxcTSbb9lUMTpFUJIXzmVL0Lrppq2Bcv1V09LB5WLCWuKrC4pGIKBA_O1Wb9O6BXhg&quot;);"
            />
            <div>
              <p class="text-base font-medium text-text-light dark:text-text-dark">
                John Smith
              </p>
              <div class="flex gap-0.5 text-accent">
                <span class="material-symbols-outlined !text-base" style="font-variation-settings: 'FILL' 1;">star</span>
                <span class="material-symbols-outlined !text-base" style="font-variation-settings: 'FILL' 1;">star</span>
                <span class="material-symbols-outlined !text-base" style="font-variation-settings: 'FILL' 1;">star</span>
                <span class="material-symbols-outlined !text-base" style="font-variation-settings: 'FILL' 1;">star</span>
                <span class="material-symbols-outlined !text-base" style="font-variation-settings: 'FILL' 1;">star</span>
              </div>
            </div>
          </div>
          <p class="text-base font-normal leading-normal text-gray-600 dark:text-gray-400">
            "The AI tutors are incredibly helpful. I can get unstuck on a problem at any time of day, which has accelerated my learning."
          </p>
        </div>
        <div class="flex flex-col gap-4 rounded-xl p-6 bg-white dark:bg-gray-800 shadow-md">
          <div class="flex items-center gap-4">
            <div
              class="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-12"
              data-alt="Portrait of Emily Jones"
              style="background-image: url(&quot;https://lh3.googleusercontent.com/aida-public/AB6AXuBpejgVpGg8Eo7_kIG2JJx2rFkoB8RrP3IpouvAd8W98co7410wHEjZ-YcKKMHJtfCqqb1fvJhwIsJZi9QzZ7k1MOiXSJ5LpOVnxcgUEfiEr9lqAkS2AJe2LSmKcEGx1kgcCMxMzCuriQY7JJ2kC9502EJu_qsia8eoUegI1-imOKLra03NwQ1Hx6gvdYO3pety3Fe8Uej-Zhco25WumRhaNMV43zJsWKrAjRK_jp68ZYlm7ylj2R0mELh4h3IthhWHqNkJQbn6vQ&quot;);"
            />
            <div>
              <p class="text-base font-medium text-text-light dark:text-text-dark">
                Emily Jones
              </p>
              <div class="flex gap-0.5 text-accent">
                <span class="material-symbols-outlined !text-base" style="font-variation-settings: 'FILL' 1;">star</span>
                <span class="material-symbols-outlined !text-base" style="font-variation-settings: 'FILL' 1;">star</span>
                <span class="material-symbols-outlined !text-base" style="font-variation-settings: 'FILL' 1;">star</span>
                <span class="material-symbols-outlined !text-base" style="font-variation-settings: 'FILL' 1;">star</span>
                <span class="material-symbols-outlined !text-base">star</span>
              </div>
            </div>
          </div>
          <p class="text-base font-normal leading-normal text-gray-600 dark:text-gray-400">
            "I love how my profile automatically updates with my new skills. It's a great way to showcase my progress to potential employers."
          </p>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>

</style>
