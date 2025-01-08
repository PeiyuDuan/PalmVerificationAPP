<template>
	<view class="content">
		<image class="logo" src="/static/logo1.jpg"></image>
		<view class="text-area">
			<text class="title">{{title}}</text>
		</view>
		<button class="register-button" @click="navigateToRegister">注册</button>
		<button class="login-button" @click="navigateToLogin">登录</button>
		<button class="recover-button" @click="navigateToRecover">找回用户名</button>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				title: '欢迎来到计算机视觉期末项目！\n 小组成员：段培煜 梁哲旭 宫辰昊'
			};
		},
		methods: {
			navigateToLogin() {
				// 跳转到登录页面
				uni.navigateTo({
					url: '/pages/login/login'
				});
			},
			navigateToRegister() {
				// 跳转到注册页面
				uni.navigateTo({
					url: '/pages/register/register'
				});
			},
			navigateToRecover() {
				uni.navigateTo({
					url: '/pages/recover/recover'
				});
			}
		}
	};
</script>

<style>
	.content {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100vh;
		background: url("../../BGpic.jpg") no-repeat center center;
		background-size: cover;
	}

	.logo {
	    height: 400rpx;
	    width: 400rpx;
	    margin-top: 100rpx;
	    margin-left: auto;
	    margin-right: auto;
	    margin-bottom: 50rpx;
	
	    background: linear-gradient(to bottom, rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.1));
	    backdrop-filter: blur(10px); /* 背景模糊效果 */
	    border-radius: 50%; /* 圆形蒙版 */
	    overflow: hidden; /* 确保内容不溢出 */
	}


	.text-area {
		display: flex;
		justify-content: center;
	}

	.title {
		font-size: 36rpx;
		color: #343436;
	}

	.login-button, .register-button, .recover-button {
		margin-top: 20rpx;
		padding: 20rpx 40rpx;
		font-size: 40rpx;
		text-align: center;
		border-radius: 20px;
		font-family: '华文中宋', sans-serif;
		color: white;
		border: none;
		width: 150px;
	}

	.login-button {
		background-color: #3d94ff;
	}

	.register-button {
		background-color: #1db1c7;
		margin-top: 15rpx;
	}
	
	.recover-button {
		background-color: #81b7c7;
		margin-top: 15rpx;
	}
</style>
