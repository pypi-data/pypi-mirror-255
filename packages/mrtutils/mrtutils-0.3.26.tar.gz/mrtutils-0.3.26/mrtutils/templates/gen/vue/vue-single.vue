<template>
    <div>
        <h1>{{msg}}</h1>
    </div>
</template>
<style >

</style>
<script>
import { ref } from 'vue'

export default {
    props: {},
    setup(props) {

        const msg = ref('hello')

        return {
            msg
        };
    },
    components: {  }
}
</script>

