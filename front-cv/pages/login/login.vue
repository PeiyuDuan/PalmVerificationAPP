<template>
  <view class="container">
    <view class="form-group">
      <text>用户名：</text>
      <input 
        type="text" 
        placeholder="请输入用户名" 
        v-model="username" 
        class="input"
      />
    </view>
    
    <view class="form-group">
      <text>上传手掌图片：</text>
      <button @click="chooseImage('image')" class="choose-button">选择图片</button>
      <image 
        v-if="image" 
        :src="image" 
        mode="aspectFit" 
        class="preview-image"
      ></image>
    </view>
    
    <button class="submit-btn" @click="submitForm">提交</button>
  </view>
</template>

<script>
import {pathToBase64} from '../../js_sdk/mmmm-image-tools/index.js'
export default {
  data() {
    return {
      username: "", // 存储用户名
      image: "", // 图片的本地路径
      imageBase64: "" // 图片的完整Base64编码（含头部）
    };
  },
  methods: {
    // 选择图片并处理
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
				this.imageBase64 = path;
			})
        },
        fail: (err) => {
            console.error('选择图片失败', err);
        }
        });
    },
	
    // 提交表单
    submitForm() {
      if (!this.username.trim()) {
        uni.showToast({
          title: '请输入用户名',
          icon: 'none'
        });
        return;
      }
      if (!this.imageBase64) {
        uni.showToast({
          title: '请选择一张图片',
          icon: 'none'
        });
        return;
      }

      // 调用后端接口
      const payload = {
        username: this.username,
        palm_image: this.imageBase64 // 提交完整Base64数据
      };
	  
	  console.log('即将发送信息:', payload)

      uni.request({
        url: 'http://192.168.151.42:5000/api/login', // 替换为你的后端接口地址
        method: 'POST',
        header: {
          'Content-Type': 'application/json'
        },
        data: payload,
        success: (res) => {
          if (res.statusCode === 200) {
            uni.showToast({
              title: '登录成功',
              icon: 'success'
            });
			console.log(res.data.hand)
          } else {
            uni.showToast({
              title: res.error || '登录失败',
              icon: 'none'
            });
			console.log(res)
          }
        },
        fail: (err) => {
          uni.showToast({
            title: '请求失败',
            icon: 'none'
          });
          console.error(err);
        }
      });
    }
  }
};
</script>

<style>
.container {
  padding: 20rpx;
  height: 100vh;
  background: url("../../BGpic.jpg") no-repeat center center;
  background-size: cover;
}
.text{
  size: 60rpx;
}
.form-group {
  margin-bottom: 30px;
  margin-top:50px;
  font-size: 40rpx;
  font-family: '华文中宋', sans-serif;
  gap: 10px;
}
.choose-button {
  width: 80%;
}
.input {
  width: 93%;
  height: 80rpx;
  border: 2px solid #515151;
  border-radius: 8rpx;
  padding: 10rpx;
  color: #333333;
}
.preview-image {
  width: 300rpx;
  height: 300rpx;
  margin-top: 20rpx;
  border: 1px solid #ccc;
  margin-left: 95px;
  border-radius: 8rpx;
}
.submit-btn {
  width: 30%;
  height: 80rpx;
  background-color: #007aff;
  color: #fff;
  text-align: center;
  line-height: 80rpx;
  border-radius: 20rpx;
}
</style>
