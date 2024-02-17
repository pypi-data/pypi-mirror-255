<script setup lang="ts">
import { NIcon, NBreadcrumbItem } from 'naive-ui'
import { DistributionIcon } from '../icons'
import { RouterLink } from 'vue-router'
</script>

<template>
    <n-breadcrumb-item>
        <router-link to="/distributions">
            <n-icon>
                <DistributionIcon />
            </n-icon>
            Distributions
        </router-link>
    </n-breadcrumb-item>
</template>