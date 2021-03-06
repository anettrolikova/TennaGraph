<template>
  <v-container class="dashboard">
    <v-layout row mt-2>
      <v-flex xs12>
        <v-layout class="d-block" px-2>

          <v-card-title v-if="eip" class="headline mb-4 mt-2 py-0 px-0 primary--text">
            <v-layout align-center>
              <nuxt-link to="/">
                <v-icon class="mr-3" medium>arrow_back</v-icon>
              </nuxt-link>
              {{ eip.eip_title }}
            </v-layout>
          </v-card-title>

          <v-card v-show="eip" class="py-4 px-4">
            <eip-description v-if="eip" :eipDescription="eip.file_content"></eip-description>
          </v-card>

          <v-card class="pt-4 pb-5 px-4 primary--text secondary_light mt-4 br-5">
            <v-card-title class="title mb-4 mt-2 py-0 px-0">
              Coinvoting | Gasvoting
            </v-card-title>
            <p class="px-2">
              You don't have to send ETH to vote. Just make a transaction with 0 ETH. Gas voting is the sum of all gas spent by an address up to the present. With one vote both the coins in that address and gas spent by that address are counted for the submitted side. Once submited it may take a few minutes to show up in the chart. To verify your address has voted click on the address link and check that your address (use ctrl-F) is in the smart contract.
            </p>
            <coinvoting :eipId="eipId" :w3="w3"></coinvoting>
          </v-card>

          <v-card class="pt-4 pb-5 px-4 primary--text secondary_light mt-4 br-5">

            <v-card-title class="title mb-4 mt-2 py-0 px-0 primary--text">
              Influencer Stances by Rank
              <v-tooltip class="mx-2" right>
                <v-icon color="grey" slot="activator">help</v-icon>
                <span>All influencers are sorted from top left to bottom right corner.</span>
              </v-tooltip>
              <v-spacer></v-spacer>
              <label class="body-1 chipTitle--text">Ranking stats by <a href="https://hive.one/ethereum" target="_blank">Hive.one</a></label>
            </v-card-title>

            <activity-chart
              v-if="isStancesLoaded"
              :yayStances="yayStances"
              :nayStances="nayStances"
              :abstainStances="abstainStances">
            </activity-chart>

            <stances-list
              v-if="isStancesLoaded && isStancesExists"
              :yayStances="yayStances"
              :nayStances="nayStances"
              :abstainStances="abstainStances">
            </stances-list>
            <v-card
              v-else
              class="secondary pa-0 primary--text secondary_light mt-4 br-5 shadow-none">
              <v-card-text  class="secondary text-xs-center py-2 px-2 noresult">
                There are no submitted stances yet
              </v-card-text>
            </v-card>
          </v-card>

          <v-card class="pt-4 pb-5 px-4 primary--text secondary_light mt-4 br-5">
            <v-card-title class="title mb-4 mt-2 py-0 px-0">
              Add a stance
              <v-tooltip class="mx-2" right>
                <v-icon color="grey" slot="activator">help</v-icon>
                <span>Your stance will be added right after passing review. All changes are stored on GitHub</span>
              </v-tooltip>
              <v-spacer></v-spacer>
            </v-card-title>
            <add-stance :eipId="eipId"></add-stance>
          </v-card>
        </v-layout>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>

  import AddStance from "~/components/AddStance";
  import commonErrorsMixin from "~/mixins/commonErrorsMixin";
  import ActivityChart from "~/components/ActivityChart";
  import StancesList from "~/components/StancesList";
  import web3Instance from "~/utils/web3Instance.js";
  import Coinvoting from "~/components/Coinvoting";
  import EipDescription from "~/components/eip/EipDescription";

  export default {
    components: {
      Coinvoting,
      StancesList,
      ActivityChart,
      AddStance,
      EipDescription,
    },
    name: "eip-details",
    mixins: [
      commonErrorsMixin,
    ],
    data() {
      return {
        eip: undefined,
        isEIPLoading: false,
        isStancesLoading: false,
        stances: [],
        eipId: this.$route.params.id,
        viewType: "0",

        yayStances: undefined,
        nayStances: undefined,
        abstainStances: undefined,
      }
    },
    created() {
      this.isEIPLoading = true;
      this.checkNetwork()
      try {
        this.loadEIP();
        this.loadInfluencers();
        this.loadStances();
      } catch (e) {
        this.setResponseErrors(e);
      }
    },
    methods: {
      async loadEIP() {
        this.isEIPLoading = true;
        try {
          this.eip = await this.$store.dispatch('eip/loadEIP', this.eipId)
        } catch (e) {
          this.setResponseErrors(e);
        }
        this.isEIPLoading = false;
      },

      async loadStances() {
        this.isStancesLoading = true;
        try {
          if (!this.isInfluencersLoaded) {
            await this.$store.dispatch('influencer/loadInfluencers')
          }
          this.stances = await this.$store.dispatch('stance/loadStances', this.eipId)
        } catch (e) {
          this.setResponseErrors(e);
        }
        this.isStancesLoading = false;
      },

      async loadInfluencers() {
        try {
          await this.$store.dispatch('influencer/loadInfluencers')
        } catch (e) {
          this.setResponseErrors(e);
        }
      },

      filterStances(stances, status) {
        return stances.filter(function (stance) {
          return stance.choice.key === status;
        })
      },

      async checkNetwork() {
        try {
          await this.w3.promisify.checkNetwork()
        } catch (e) {

          this.setErrors(e.message)
        }
      }
    },
    computed: {
      isInfluencersLoaded() {
        return this.$store.getters['influencer/']
      },
      isStancesLoaded() {
        return this.yayStances && this.nayStances && this.abstainStances;
      },
      isStancesExists() {
        return this.yayStances.length != 0 || this.nayStances.length != 0 || this.abstainStances.length != 0
      },
      w3() {
        return web3Instance
      }
    },
    watch: {
      stances(newValue) {
        this.yayStances = this.filterStances(newValue, 'YAY')
        this.nayStances = this.filterStances(newValue, 'NAY')
        this.abstainStances = this.filterStances(newValue, 'ABSTAIN')
      }
    }
  }
</script>

<style scoped>

</style>
