import { createRouter, createWebHashHistory } from 'vue-router'
import { isAuthenticated, verifyToken, logout } from '@/utils/auth'
import HomePage from '@/pages/HomePage.vue'
import LoginPage from '@/pages/LoginPage.vue'
import AdminLayout from '@/components/AdminLayout.vue'
import PetManagePage from '@/pages/PetManagePage.vue'
import AnnouncementManagePage from '@/pages/AnnouncementManagePage.vue'
import AccountManagePage from '@/pages/AccountManagePage.vue'
import MessageManagePage from '@/pages/MessageManagePage.vue'

const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomePage
        },
        {
            path: '/login',
            name: 'login',
            component: LoginPage
        },
        {
            path: '/admin',
            component: AdminLayout,
            redirect: '/admin/pets',
            children: [
                {
                    path: 'pets',
                    name: 'admin-pets',
                    component: PetManagePage
                },
                {
                    path: 'announcement',
                    name: 'admin-announcement',
                    component: AnnouncementManagePage
                },
                {
                    path: 'accounts',
                    name: 'admin-accounts',
                    component: AccountManagePage
                },
                {
                    path: 'messages',
                    name: 'admin-messages',
                    component: MessageManagePage
                }
            ]
        }
    ]
})

router.beforeEach(async (to) => {
    if (to.path.startsWith('/admin')) {
        if (!isAuthenticated()) {
            return { name: 'login' }
        }
        const valid = await verifyToken()
        if (!valid) {
            logout()
            return { name: 'login' }
        }
    }
})

export default router