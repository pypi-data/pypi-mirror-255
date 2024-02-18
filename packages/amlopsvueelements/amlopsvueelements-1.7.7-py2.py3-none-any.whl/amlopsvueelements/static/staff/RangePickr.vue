<script setup lang="ts">
import { defineProps, defineModel, computed, watch } from 'vue'
import moment from 'moment-timezone'

import { FlatPickr, SelectField } from 'shared/components'
import TimeAutoComplete from '@/components/common/TimeAutoComplete.vue'

interface Props {
  maxDiff: number // in hours
  timezoneOptions?: { label: string; value: string }[]
  isLoadingTimezoneOptions?: boolean
  allDay?: boolean
  readonly?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  maxDiff: 0,
  allDay: false,
  readonly: false,
  disabled: false
})
const model = defineModel<Date[] | string[]>('range')
const timezone = defineModel<string>('timezone')

const updateModelValue = (
  nStartDate: string,
  nStartTime: string,
  nEndDate: string,
  nEndTime: string
) => {
  if (props.allDay) {
    model.value = [nStartDate, nEndDate]
  } else {
    model.value = [
      moment
        .tz(nStartDate, 'YYYY-MM-DD', timezone.value ?? 'UTC')
        .add(moment.duration(nStartTime))
        .tz('UTC')
        .format('YYYY-MM-DD HH:mm:ss'),
      moment
        .tz(nEndDate, 'YYYY-MM-DD', timezone.value ?? 'UTC')
        .add(moment.duration(nEndTime))
        .tz('UTC')
        .format('YYYY-MM-DD HH:mm:ss')
    ]
  }
}

// Automatically adjust the endDate & endTime to maintain the time difference with the startDate & startTime.
const getAdjustedEndDatetime = (
  [newStartDate, newStartTime]: string[],
  [oldStartDate, oldStartTime]: string[]
): string[] => {
  if (props.allDay) {
    return [newStartDate, endTime.value]
  } else {
    const endDatetime = moment(endDate.value, 'YYYY-MM-DD').add(moment.duration(endTime.value)),
      oldStartDatetime = moment(oldStartDate, 'YYYY-MM-DD').add(moment.duration(oldStartTime)),
      diff = moment.duration(endDatetime.diff(oldStartDatetime)),
      newEndDatetime = moment(newStartDate, 'YYYY-MM-DD')
        .add(moment.duration(newStartTime))
        .add(diff)

    if (diff.asHours() <= 0) {
      if (diff.asHours() < -props.maxDiff) {
        const newStartDateTime = moment(newStartDate, 'YYYY-MM-DD').add(
            moment.duration(newStartTime)
          ),
          newEndDatetime = moment(newStartDateTime).add(props.maxDiff, 'hours')
        return [newEndDatetime.format('YYYY-MM-DD'), newEndDatetime.format('HH:mm')]
      }
      return [endDate.value, endTime.value]
    } else {
      return [newEndDatetime.format('YYYY-MM-DD'), newEndDatetime.format('HH:mm')]
    }
  }
}

const startDate = computed<string>({
  get() {
    return moment
      .tz(model.value?.[0], 'UTC')
      .tz(timezone.value ?? 'UTC')
      .format('YYYY-MM-DD')
  },
  set(newValue) {
    const [newEndDate, newEndTime] = getAdjustedEndDatetime(
      [newValue, startTime.value],
      [startDate.value, startTime.value]
    )
    updateModelValue(newValue, startTime.value, newEndDate, newEndTime)
  }
})
const startTime = computed<string>({
  get() {
    return moment
      .tz(model.value?.[0], 'UTC')
      .tz(timezone.value ?? 'UTC')
      .format('HH:mm')
  },
  set(newValue) {
    const [newEndDate, newEndTime] = getAdjustedEndDatetime(
      [startDate.value, newValue],
      [startDate.value, startTime.value]
    )
    updateModelValue(startDate.value, newValue, newEndDate, newEndTime)
  }
})
const endDate = computed<string>({
  get() {
    return moment
      .tz(model.value?.[1], 'UTC')
      .tz(timezone.value ?? 'UTC')
      .format('YYYY-MM-DD')
  },
  set(newValue) {
    updateModelValue(startDate.value, startTime.value, newValue, endTime.value)
  }
})
const endTime = computed<string>({
  get() {
    return moment
      .tz(model.value?.[1], 'UTC')
      .tz(timezone.value ?? 'UTC')
      .format('HH:mm')
  },
  set(newValue) {
    updateModelValue(
      startDate.value,
      startTime.value,
      moment(endDate.value).isSame(moment(startDate.value)) &&
        moment(newValue, 'HH:mm').isBetween(
          moment('00:00', 'HH:mm'),
          moment(startTime.value, 'HH:mm'),
          undefined,
          '[)'
        )
        ? moment(endDate.value).add(1, 'day').format('YYYY-MM-DD') // When selecting a time for the next date, update the endDate accordingly.
        : endDate.value,
      newValue
    )
  }
})

const startDatetimeUTC = computed(() => {
  return moment
    .tz(startDate.value, 'YYYY-MM-DD', timezone.value ?? 'UTC')
    .add(moment.duration(startTime.value))
    .tz('UTC')
    .format('YYYY-MM-DD HH:mm UTC')
})
const endDatetimeUTC = computed(() => {
  return moment
    .tz(endDate.value, 'YYYY-MM-DD', timezone.value ?? 'UTC')
    .add(moment.duration(endTime.value))
    .tz('UTC')
    .format('YYYY-MM-DD HH:mm UTC')
})

watch(
  () => props.allDay,
  () => {
    if (props.allDay && startDate?.value) {
      endDate.value = startDate.value
    }
  }
)
</script>

<template>
  <div class="mb-[1rem]">
    <div class="flex align-items-center gap-x-2">
      <div class="flex border rounded-[8px] date-time-picker overflow-hidden">
        <FlatPickr
          :config="{
            allowInput: true,
            altInput: true,
            altFormat: 'Y-m-d',
            locale: { firstDayOfWeek: 1 }
          }"
          class="flex-[2]"
          v-model="startDate"
          placeholder=""
          :disabled="disabled"
        />
        <TimeAutoComplete v-model="startTime" class="flex-1" v-if="!allDay" />
      </div>
      <span> - </span>
      <div class="flex border rounded-[8px] date-time-picker overflow-hidden">
        <TimeAutoComplete
          v-model="endTime"
          :from="moment(endDate).isSame(moment(startDate)) ? startTime : undefined"
          :max-time="
            moment(endDate).isSame(moment(startDate))
              ? undefined
              : moment(startDate).add(moment.duration(startTime)).add(1, 'day').format('HH:mm')
          "
          class="flex-1"
          v-if="!allDay"
        />
        <FlatPickr
          :config="{
            allowInput: true,
            altInput: true,
            altFormat: 'Y-m-d',
            locale: { firstDayOfWeek: 1 }
          }"
          class="flex-[2]"
          v-if="allDay || startDate !== endDate"
          v-model="endDate"
          placeholder=""
          :disabled="disabled"
        />
      </div>
    </div>
    <small class="text-body-secondary form-text italic" v-if="!allDay">
      ({{ startDatetimeUTC }}) - ({{ endDatetimeUTC }})
    </small>
  </div>
  <div class="mb-[1rem] flex gap-x-2 align-items-center">
    <div class="form-check w-[100px]">
      <input
        :checked="allDay"
        readonly
        disabled
        class="form-check-input"
        type="checkbox"
        id="all-day-check"
      />
      <label class="form-check-label !mb-0" for="all-day-check"> All day </label>
    </div>
    <SelectField
      :options="timezoneOptions"
      :reduce="(option: any) => option.value"
      label="label"
      :loading="isLoadingTimezoneOptions"
      v-model="timezone"
      :clearable="false"
      :append-to-body="false"
      placeholder=""
      class="mb-0 flex-1"
      v-if="!allDay"
    />
  </div>
</template>

<style scoped lang="scss">
:deep(input.leg-date-picker) {
  height: 2.5rem !important;
  padding: 5px 1rem !important;
  border: none !important;
  border-radius: unset !important;
  outline: unset;
  ::placeholder {
    text-align: center;
  }

  &:focus {
    box-shadow: unset;
    background-color: #88888838;
  }
  &:hover {
    background-color: #88888838;
  }
}
.date-time-picker:hover {
  box-shadow:
    0 1px 2px 0 rgba(0, 0, 0, 0.07),
    0 0 0 0.18rem rgba(81, 93, 138, 0.25);
}
</style>
