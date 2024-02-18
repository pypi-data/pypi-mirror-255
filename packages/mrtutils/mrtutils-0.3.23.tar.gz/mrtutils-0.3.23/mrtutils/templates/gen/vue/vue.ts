import { ref } from 'vue'

export default {
    props: {},
    setup() {

        const msg = ref('hello')

        return {
            msg
        };
    },
    components: {  }
}