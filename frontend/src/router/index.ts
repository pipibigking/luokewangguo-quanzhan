import { createRouter, createWebHashHistory } from 'vue-router'
import { isAuthenticated } from '@/utils/auth'

const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        {
            path: '/',
            name: 'home',
            component: () => import('@/pages/HomePage.vue')
        },
        {
            path: '/login',
            name: 'login',
            component: () => import('@/pages/LoginPage.vue')
        },
        {
            path: '/admin',
            component: () => import('@/components/AdminLayout.vue'),
            redirect: '/admin/pets',
            children: [
                {
                    path: 'pets',
                    name: 'admin-pets',
                    component: () => import('@/pages/PetManagePage.vue')
                },
                {
                    path: 'announcement',
                    name: 'admin-announcement',
                    component: () => import('@/pages/AnnouncementManagePage.vue')
                },
                {
                    path: 'accounts',
                    name: 'admin-accounts',
                    component: () => import('@/pages/AccountManagePage.vue')
                }
            ]
        }
    ]
})

router.beforeEach((to) => {
    if (to.path.startsWith('/admin')) {
        if (!isAuthenticated()) {
            return { name: 'login' }
        }
    }
})

export default router
