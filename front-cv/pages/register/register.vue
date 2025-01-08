<template>
  <view class="container">
    <!-- 页面标题 -->
    <view class="header">
      <text class="title">Register</text>
    </view>

    <!-- 用户名输入框 -->
    <view class="input-section">
      <input 
        class="input-box" 
        placeholder="请输入用户名" 
        v-model="username" 
      />
    </view>

    <!-- 上传图片区域 -->
    <view class="upload-section">
      <view class="upload-item">
        <button @click="chooseImage('image1')">拍照上传左手掌图片</button>
        <image v-if="image1" :src="image1" class="preview"></image>
      </view>
      <view class="upload-item">
        <button @click="chooseImage('image2')">拍照上传右手掌图片</button>
        <image v-if="image2" :src="image2" class="preview"></image>
      </view>
    </view>

    <!-- 提交按钮 -->
    <button class="submit-btn" @click="submit">提交</button>
  </view>
</template>

<script>
import {pathToBase64} from '../../js_sdk/mmmm-image-tools/index.js'
export default {
  data() {
    return {
      username: "", // 用户名
      image1: "", // 左手掌图片路径
      image2: "", // 右手掌图片路径
      image1Base64: "", // 左手掌图片的Base64
      image2Base64: ""  // 右手掌图片的Base64
    };
  },
  methods: {
    // 选择图片
    chooseImage(imageKey) {
        uni.chooseImage({
        count: 1, // 选择1张图片
        sourceType: ['camera'], // 从相册或相机选择
        sizeType: ['original', 'compressed'], // 选择原图或者压缩图
        success: (res) => {
    		const filePath = res.tempFilePaths[0]; // 选中的图片路径
    		this[imageKey] = filePath; // 保存图片路径
    		// 通过 FileReader 将图片转换为 Base64
    		pathToBase64(filePath)
    		.then(path=>{
    			this[`${imageKey}Base64`] = path;
    		})
        },
        fail: (err) => {
            console.error('选择图片失败', err);
        }
        });
    },

    // 提交数据
    submit() {
      if (!this.username.trim()) {
        uni.showToast({
          title: "请输入用户名",
          icon: "none"
        });
        return;
      }

      if (!this.image1Base64 || !this.image2Base64) {
        uni.showToast({
          title: "请先上传两张手掌图片",
          icon: "none"
        });
        return;
      }

      const payload = {
        username: this.username,
        left_palm_image: this.image1Base64, // 确保字段名和后端一致
        right_palm_image: this.image2Base64 // 确保字段名和后端一致
      };

      console.log("即将发送数据:", payload); // 调试输出

      uni.request({
        url: 'http://192.168.151.42:5000/api/register', // 替换为实际后端接口
        method: 'POST',
        data: payload,
        header: {
          'Content-Type': 'application/json'
        },
        success: (res) => {
          if (res.statusCode === 200) {
            uni.showToast({
              title: "注册成功",
              icon: "success"
            });
          } else {
            uni.showToast({
              title: "提交失败，请重试",
              icon: "none"
            });
            console.error("提交失败：", res.data);
          }
        },
        fail: (err) => {
          uni.showToast({
            title: "网络错误",
            icon: "none"
          });
          console.error("请求失败：", err);
        }
      });
    }
  }
};
</script>

<style>
.container {
  padding: 20px;
  height: 100vh;
  background: url("../../BGpic.jpg") no-repeat center center;
  background-size: cover;
}
.header {
  margin-top:50px;
  margin-bottom: 20px;
  text-align: center;
}
.title {
  font-size: 24px;
  font-weight: bold;
  font-family: '华文中宋', sans-serif;
}
.input-section {
  margin-bottom: 20px;
}
.input-box {
  width: 93%;
  padding: 10px;
  border: 2px solid #515151;
  border-radius: 5px;
  font-size: 16px;
  color: #333333;
}
.upload-section {
  margin-bottom: 40px;
  display: auto;
  justify-content: center;
  align-items: center;
}
.upload-item {
  margin-bottom: 15px;
  margin-left:30px;
  justify-content: center;
  align-items: center;
  width: 250px;
}
.preview {
  width: 100px;
  height: 100px;
  margin-top: 10px;
  border: 2px solid #ccc;
  border-radius: 5px;
  margin-left: 70px;
}
.submit-btn {
  padding: 10px 0;
  background-color: #007AFF;
  color: white;
  font-size: 16px;
  text-align: center;
  border: none;
  border-radius: 20px;
  width: 150px;
}
</style>
