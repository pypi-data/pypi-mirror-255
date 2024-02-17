### 安装
```shell
pip install lxml -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
pip install pyquery -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
pip install lesscpy -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
pip install calmjs.parse -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
```
### 模板示例：
``` vue
<template>
    <div>
        <div class="app">{{ message }}</div>
        <img data-src="https://img2.baidu.com/it/u=142041029,119347019&fm=253&fmt=auto&app=138&f=JPG?w=667&h=500">
    </div>
</template>

<script src="http://127.0.0.1:18080/static/js/base.js"></script>
<script>
export default{
    data:{
        message:'hello test'
    }, methods: {
        init:function(){
            img_delay_down_handle();
        }
    }
}
</script>

<style>
.app {
  color: red;
  font-weight: bold;
}
</style>
```
### 使用格式化模板
```python
from afeng_tools.template_tool import template_tools

if __name__ == '__main__':
    html_code, js_code, css_code = template_tools.render('index.html')
    with open('tmp.html', 'w', encoding='utf-8') as f:
        f.write('<html>')
        f.write(css_code)
        f.write('<body>')
        f.write(html_code)
        f.write(js_code)
        f.write('</body>')
        f.write('</html>')
```
结果：
```html
<html><style>#template_index .app{color:red;font-weight:bold;}</style><body><div id="template_index"><div>
 <div class="app">
  {{ message }}
 </div>
 <img data-src="https://img2.baidu.com/it/u=142041029,119347019&amp;fm=253&amp;fmt=auto&amp;app=138&amp;f=JPG?w=667&amp;h=500"/>
</div>
</div><script src="http://127.0.0.1:18080/static/js/base.js"></script><script>var template_index={data:{message:'hello test'},methods:{init:function(){img_delay_down_handle();}}};template_index.methods.init();</script></body></html>
```