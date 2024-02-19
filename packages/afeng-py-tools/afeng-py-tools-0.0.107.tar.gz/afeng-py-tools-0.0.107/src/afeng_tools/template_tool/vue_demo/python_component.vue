<template>
    <div>
        {{name}} ({{originalName}})
        <button @click="inc(3)">+3</button>
        <button @click="inc()">+1</button>
        {{cpt}} : {{ccpt}} {{wcpt}}
    </div>
</template>
<script lang="python">
class Component:

    def __init__(self, name="?"):
        print("DATA INIT",name)
        self.cpt=0
        self.wcpt=""
        self.originalName=name  # copy the $props.name

    def inc(self,nb=1):                 # with py3, you can make this a async method !
        print("inc(%s)"%nb,self.name)
        self.cpt+=nb

    def CREATED(self):
        print("CREATED",self.name)

    def UPDATED(self):
        print("UPDATED",self.name)

    def MOUNTED(self):
        print("mounted",self.name,"in",self["$parent"]["$options"].name)
        self.inc()

    def COMPUTED_ccpt(self):
        print("COMPUTE",self.name,self.cpt,"changed")
        return self.cpt*"#"

    def WATCH_1(self,newVal,oldVal,name="cpt"):
        print("WATCH",self.name,name,oldVal,"-->",newVal)
        self.wcpt=self.cpt*"+"

    def WATCH_2(self,newVal,oldVal,name="name"):    # watch the prop !
        print("WATCH",name,oldVal,"-->",newVal)

</script>