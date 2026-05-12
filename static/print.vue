<template id="page-offlineshop-print">
  <div class="row justify-center">
    <div v-for="item in items" :key="item.url" class="q-my-sm q-mx-lg">
      <div class="text-center q-ma-none q-mb-sm">
        <span v-text="item.name"></span>
      </div>
      <lnbits-qrcode
        :value="setBech32(item.url)"
        :show-buttons="false"
      ></lnbits-qrcode>
      <div class="text-center q-ma-none q-mt-sm">
        <span v-text="item.price"></span>
      </div>
    </div>
  </div>
</template>
