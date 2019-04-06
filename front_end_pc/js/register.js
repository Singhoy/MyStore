let vm;
vm = new Vue({
    el: '#app',
    data: {
        error_name: false,
        error_password: false,
        error_check_password: false,
        error_phone: false,
        error_allow: false,
        error_image_code: false,
        error_sms_code: false,

        username: '',
        password: '',
        password2: '',
        mobile: '',
        image_code: '',
        image_code_url: '',
        sms_code: '',
        allow: false,

        host,

        image_code_error_message: '请填写图片验证码',
        sms_code_tip: '获取短信验证码',
        get_sms_tip: '请填写短信验证码',
        username_tip: '',
        phone_tip: '请输入手机号码',
        sending_flag: false
    },
    mounted() {
        this.generate_code_url();
    },
    methods: {
        generate_code_url() {
            this.code_id = this.generate_uuid();
            this.image_code_url = this.host + 'image_codes/' + this.code_id + '/';
        },
        generate_uuid() {
            let d = new Date().getTime();
            if (window.performance && typeof window.performance.now === 'function') {
                d += performance.now();
            }
            return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
                let r = (d + Math.random() * 16) % 16 | 0;
                d = Math.floor(d / 16);
                return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
            });
        },
        send_sms() {
            this.check_phone();
            this.check_image_code();
            if (this.error_phone || this.error_image_code) {
                return;
            }
            if (this.sending_flag == true) {
                return;
            }
            let url = this.host + 'sms_codes/' + this.mobile + '/?image_code_id=' + this.code_id + '&text=' + this.image_code;
            axios.get(url).then(resp => {
                this.sending_flag = true;
                let num = 60;
                let t = setInterval(() => {
                    if (num == 1) {
                        clearInterval(t);
                        this.sms_code_tip = '获取短信验证码';
                        this.sending_flag = false;
                    } else {
                        num -= 1;
                        this.sms_code_tip = num + '秒';
                    }
                }, 1000)
            }).catch(err => {
                if (err.response.status == 400) {
                    this.image_code_error_message = '图片验证码有误';
                    this.error_image_code = true;
                } else {
                    console.log(err.response.status);
                }
                this.sending_flag = false;
            })
        },
        check_username() {
            const len = this.username.length;
            const re = /^\d{5,}$/;
            if (len < 5 || len > 20 || re.test(this.username)) {
                this.error_name = true;
                this.username_tip = '请输入5-20个字符的用户名，不能是纯数字'
            } else this.error_name = false;
            let url;
            if (!this.error_name) {
                url = this.host + 'usernames/' + this.username + '/count/';
                axios.get(url, {responseType: 'json'}).then(response => {
                    if (response.data.count == '0') {
                        this.error_name = false;
                        this.username_tip = '用户名可以注册'
                    } else {
                        this.error_name = true;
                        this.username_tip = '用户名已存在'
                    }
                }).catch(error => {
                    console.log(error.data)
                })
            }
        },
        check_pwd() {
            const len = this.password.length;
            this.error_password = len < 8 || len > 20;
        },
        check_cpwd() {
            this.error_check_password = this.password != this.password2;
        },
        check_phone() {
            const re = /^1[345789]\d{9}$/;
            this.error_phone = !re.test(this.mobile);
        },
        check_image_code() {
            this.error_image_code = !this.image_code;
        },
        check_sms_code() {
            this.error_sms_code = !this.sms_code;
        },
        check_allow() {
            this.error_allow = !this.allow;
        },
        // 注册
        on_submit() {
            this.check_username();
            this.check_pwd();
            this.check_cpwd();
            this.check_phone();
            this.check_sms_code();
            this.check_allow();
        }
    }
});
