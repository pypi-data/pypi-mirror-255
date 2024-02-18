<script setup lang="ts">
import { computed, nextTick, reactive, ref, watch } from 'vue'
// @ts-ignore
import { useVuelidate } from '@vuelidate/core'
import { required, requiredIf, helpers } from '@vuelidate/validators'
import type { DateSelectArg } from '@fullcalendar/core'
import type { AxiosError } from 'axios'
import moment from 'moment-timezone'
import { useMutation } from '@tanstack/vue-query'
import { getFlooredTime } from '@/utils/date'

import {
  BAlert,
  BButton,
  BForm,
  BFormGroup,
  BFormInvalidFeedback,
  BFormTextarea,
  BModal
} from 'bootstrap-vue-next'
import { FlatPickr, SelectField } from 'shared/components'
import ApplyDatesSelect from '@/components/common/ApplyDatesSelect.vue'
import RangePickr from '@/components/calendar/RangePickr.vue'

import type { EventApi } from '@fullcalendar/core'
import type { Person } from '@/models/Person'
import type {
  SpecificEntryPayload,
  SpecificEntryPersonPopulated,
  BlanketEntryPersonPopulated,
  BlanketEntryPayload
} from '@/models/Entry'
import type { EntryType } from '@/models/EntryType'
import { useTimezones } from '@/composables/useTimezones'
import { usePeople } from '@/composables/usePeople'
import { useEntryTypes } from '@/composables/useEntryTypes'

import entryService from '@/services/EntryService'

import ApplyDaysSelect from '@/components/common/ApplyDaysSelect.vue'
import ApplyWeeksSelect from '@/components/common/ApplyWeeksSelect.vue'
import ConfirmModal, { type ConfirmOption } from '@/components/calendar/ConfirmModal.vue'

export type EventEditMode = 'add' | 'quick-add-sickness-absence' | 'edit'

type RepeatFreq = 'no-repeat' | 'daily' | 'weekly'
interface RepeatFreqOption {
  label: string
  value: RepeatFreq
}

interface Props {
  mode?: EventEditMode
  event?: EventApi
  selectionInfo?: DateSelectArg
}

interface FormValues {
  id: number | undefined
  person: Person | undefined
  entry_type: EntryType | undefined
  range: string[] | undefined
  timezone: string
  repeatFreq: RepeatFreq
  until: string | undefined
  applied_on_dates: number[] | undefined
  applied_on_days: number[] | undefined
  applied_on_weeks: number[] | undefined
  comment: string | undefined
  replaces_other_entry: number | null | undefined
  replaces_own_entry: number | null | undefined
}

const defaultValues: FormValues = {
  id: undefined,
  person: undefined,
  entry_type: undefined,
  range: [],
  timezone: 'UTC', // TODO: Remove it (Bind directly to the person's timezone)
  repeatFreq: 'no-repeat',
  until: '',
  applied_on_dates: undefined,
  applied_on_days: undefined,
  applied_on_weeks: [0],
  comment: undefined,
  replaces_other_entry: undefined,
  replaces_own_entry: undefined
}

const open = defineModel<boolean>('open')
const props = withDefaults(defineProps<Props>(), {
  mode: 'add'
})
const emit = defineEmits(['event-created', 'hide'])

const { data: timezones, isLoading: isLoadingTimezones } = useTimezones()
const { data: people, isLoading: isLoadingPeople } = usePeople()
const { data: entryTypes, isLoading: isLoadingEntryTypes } = useEntryTypes()

const isDelete = ref<boolean>(false)
const isConfirmModalOpen = ref<boolean>(false)

const repeatFreqOptions = computed<RepeatFreqOption[]>(() => [
  {
    label: "Doesn't repeat",
    value: 'no-repeat'
  },
  {
    label: 'Daily',
    value: 'daily'
  },
  {
    label: 'Weekly',
    value: 'weekly'
  }
])
const isBlanketEntry = computed(() => {
  return props.event?.id.startsWith('blanket') ?? false
})
const entry = computed<SpecificEntryPersonPopulated | BlanketEntryPersonPopulated>(
  () => props.event?.extendedProps as SpecificEntryPersonPopulated | BlanketEntryPersonPopulated
)

const { isPending, mutate } = useMutation({
  mutationFn: ({
    entries,
    isDelete
  }: {
    entries: SpecificEntryPayload[] | BlanketEntryPayload[]
    isDelete?: boolean
  }) =>
    values.repeatFreq === 'weekly'
      ? isDelete
        ? entryService.deleteBlanketEntries(entries)
        : props.mode === 'edit'
          ? entryService.updateBlanketEntries(entries)
          : entryService.createBlanketEntries(entries)
      : isDelete
        ? entryService.deleteSpecificEntries(entries)
        : props.mode === 'edit'
          ? entryService.updateSpecificEntries(entries)
          : entryService.createSpecificEntries(entries),
  onSuccess: (data) => {
    emit('event-created', data)
    open.value = false
  },
  onError: (error: AxiosError) => {
    if (!error.response) {
      non_field_errors.value = ['Network error']
      return
    }

    const errors = (error.response.data as any).errors
      ? (error.response.data as any).errors[0]
      : undefined
    if (!errors) {
      non_field_errors.value = ['Unknown error']
    } else if (errors.non_field_errors) {
      non_field_errors.value = errors.non_field_errors
    } else if (errors.message) {
      non_field_errors.value = [errors.message]
    } else {
      $externalResults.value = errors
    }
  }
})

const non_field_errors = ref<string[]>([])
const $externalResults = ref({})

const rules = computed(() => ({
  id: {},
  person: { required },
  entry_type: { required },
  range: {
    required,
    lessInvalid: helpers.withMessage(
      () => 'The event must end after its start',
      (range: Date[] | string[]) => {
        if (!range || range.length !== 2) {
          return true
        }

        return values.entry_type?.requires_full_workday
          ? moment(range[0]).isSameOrBefore(moment(range[1]))
          : moment(range[0]).isBefore(moment(range[1]))
      }
    ),
    overInvalid: helpers.withMessage(
      () => 'The event duration must not exceed 24 hours',
      (range: Date[] | string[]) => {
        if (!range || range.length !== 2) {
          return true
        }

        return moment.duration(moment(range[1]).diff(range[0])).asHours() < 24
      }
    )
  },
  timezone: {},
  repeatFreq: { required },
  until: { requiredIf: requiredIf(values.repeatFreq !== 'no-repeat') },
  // applied_on_dates: {},
  applied_on_dates: { requiredUnless: requiredIf(values.repeatFreq === 'daily') },
  applied_on_days: { requiredIf: requiredIf(values.repeatFreq === 'weekly') },
  applied_on_weeks: { requiredIf: requiredIf(values.repeatFreq === 'weekly') },
  comment: { requiredIf: requiredIf(values.entry_type?.requires_comment ?? false) },
  replaces_other_entry: {},
  replaces_own_entry: {}
}))
const values = reactive<FormValues>({
  id: defaultValues.id,
  person: defaultValues.person,
  entry_type: defaultValues.entry_type,
  range: defaultValues.range,
  timezone: defaultValues.timezone,
  repeatFreq: defaultValues.repeatFreq,
  until: defaultValues.until,
  applied_on_dates: defaultValues.applied_on_dates,
  applied_on_days: defaultValues.applied_on_days,
  applied_on_weeks: defaultValues.applied_on_weeks,
  comment: defaultValues.comment,
  replaces_other_entry: defaultValues.replaces_other_entry,
  replaces_own_entry: defaultValues.replaces_own_entry
})
const v$ = useVuelidate(rules, values, { $externalResults, $autoDirty: true })

const selectAppliedOnWeeks = (action: ConfirmOption) => {
  // The week number starting from start_date of event
  let weekno = 0
  for (
    const iDate = moment(values.range?.[0]).startOf('week');
    iDate.isSameOrBefore(props.event?.start);
    iDate.add(1, 'week')
  ) {
    weekno++
  }
  let weeks: number[]
  if (action === 'only') {
    weeks = [weekno]
  } else if (action === 'following') {
    const index = values?.applied_on_weeks?.indexOf(weekno)
    weeks = values.applied_on_weeks?.slice(index) ?? []
  } else {
    weeks = values.applied_on_weeks ?? []
  }
  return weeks
}

const selectAppliedOnDates = (action?: ConfirmOption) => {
  const date = moment(props.event?.start).get('date')

  let dates: number[]
  if (action === 'only') {
    dates = [date]
  } else if (action === 'following') {
    const index = values.applied_on_dates?.indexOf(date)
    dates = values.applied_on_dates?.slice(index) ?? []
  } else {
    dates = values.applied_on_dates ?? []
  }

  return dates
}

const onConfirm = (action: ConfirmOption) => {
  const entryPayload: SpecificEntryPayload | BlanketEntryPayload = {
    id: values.id,
    person: values.person?.person_id,
    team: values.person?.aml_team_id,
    start_hour: values.entry_type?.requires_full_workday
      ? '00:00:00'
      : moment(values.range?.[0]).format('HH:mm:ss'),
    end_hour: values.entry_type?.requires_full_workday
      ? '23:59:59'
      : moment(values.range?.[1]).format('HH:mm:ss'),
    comment: values.comment,
    start_date: moment(values.range?.[0]).format('YYYY-MM-DD'),
    end_date:
      values.repeatFreq === 'no-repeat'
        ? moment(values.range?.[0]).format('YYYY-MM-DD')
        : values.until,
    entry_type: values.entry_type?.id,
    ...(values.repeatFreq === 'weekly'
      ? {
          applied_on_days: values.applied_on_days,
          applied_on_weeks: values.applied_on_weeks
        }
      : {
          applied_on_dates: values.applied_on_dates
        })
  }

  // Edit
  if (props.mode === 'edit') {
    entryPayload.flagged_for_edit = entry.value?.flagged_for_edit
    entryPayload.flagged_for_delete = entry.value?.flagged_for_delete
    if (isDelete.value) {
      entryPayload.flagged_for_delete = true
    } else {
      entryPayload.flagged_for_edit = true
    }

    if (values.repeatFreq === 'weekly') {
      if ('applied_on_weeks' in entryPayload) {
        entryPayload.applied_on_weeks = selectAppliedOnWeeks(action)
      }
    } else {
      if ('applied_on_dates' in entryPayload) {
        entryPayload.applied_on_dates = selectAppliedOnDates(action)
      }
    }
  }
  // Add
  else {
    if (values.repeatFreq === 'daily') {
      const availableDates: number[] = []
      for (
        const iDate = moment(values.range?.[0]);
        iDate.isSameOrBefore(values.until);
        iDate.add(1, 'day')
      ) {
        if (availableDates.length === 31) {
          break
        }

        const date = iDate.get('date')
        if (availableDates.includes(date)) {
          continue
        }
        availableDates.push(date)
      }
      availableDates.sort((a, b) => a - b)
      if ('applied_on_dates' in entryPayload) {
        entryPayload.applied_on_dates = availableDates
      }
    } else if (values.repeatFreq === 'no-repeat') {
      if ('applied_on_dates' in entryPayload) {
        entryPayload.applied_on_dates = [moment(values.range?.[0]).get('date')]
      }
    }
  }
  mutate({ entries: [entryPayload], isDelete: isDelete.value })
}

const onSubmit = async () => {
  const isValid = await v$?.value?.$validate()
  non_field_errors.value = []

  if (!isValid) {
    return
  }

  isDelete.value = false
  if (props.mode === 'edit') {
    if (values.repeatFreq === 'no-repeat') {
      onConfirm('all')
    } else {
      isConfirmModalOpen.value = true
    }
  } else {
    onConfirm('all')
  }
}

const onCancel = () => {
  open.value = false
}

const onDelete = () => {
  isDelete.value = true
  if (values.repeatFreq === 'no-repeat') {
    onConfirm('all')
  } else {
    isConfirmModalOpen.value = true
  }
}

const resetForm = async () => {
  // Edit
  if (entry.value) {
    values.id = entry.value.id
    values.person = entry.value.person
    values.entry_type = entry.value.entry_type
    values.range = [
      `${entry.value.start_date}T${entry.value.start_hour}Z`,
      `${
        moment(entry.value.end_hour, 'HH:mm:ss').isBefore(
          moment(entry.value.start_hour, 'HH:mm:ss')
        )
          ? moment(entry.value.start_date, 'YYYY-MM-DD').add(1, 'day').format('YYYY-MM-DD')
          : entry.value.start_date
      }T${entry.value.end_hour}Z`
    ]
    values.timezone = entry.value.person.timezone ?? 'UTC'

    await nextTick()
    values.repeatFreq = isBlanketEntry.value
      ? 'weekly'
      : entry.value.start_date === entry.value.end_date
        ? 'no-repeat'
        : 'daily'
    values.until = entry.value.end_date
    if ('applied_on_dates' in entry.value) {
      values.applied_on_dates = entry.value.applied_on_dates
    }
    if ('applied_on_days' in entry.value) {
      values.applied_on_days = entry.value.applied_on_days
    }
    if ('applied_on_weeks' in entry.value) {
      values.applied_on_weeks = entry.value.applied_on_weeks
    }
    values.comment = entry.value.comment
    if ('replaces_other_entry' in entry.value) {
      values.replaces_other_entry = entry.value.replaces_other_entry
    }
    if ('replaces_own_entry' in entry.value) {
      values.replaces_own_entry = entry.value.replaces_own_entry
    }
  }
  // Add
  else {
    const currentTimeFloored = getFlooredTime(moment()).tz('UTC')

    values.id = defaultValues.id
    values.person = props.selectionInfo
      ? props.selectionInfo.resource?.extendedProps.person
      : defaultValues.person
    values.entry_type = defaultValues.entry_type
    values.range = props.selectionInfo
      ? [
          moment(props.selectionInfo.start)
            .tz(props.selectionInfo.resource?.extendedProps.person.timezone ?? 'UTC')
            .format('YYYY-MM-DD HH:mm:ss'),
          moment(props.selectionInfo.end)
            .subtract(props.selectionInfo.allDay ? 1 : 0, 'minutes')
            .tz(props.selectionInfo.resource?.extendedProps.person.timezone ?? 'UTC')
            .format('YYYY-MM-DD HH:mm:ss')
        ]
      : [
          currentTimeFloored.format('YYYY-MM-DD HH:mm:ss'),
          moment(currentTimeFloored).add(1, 'hour').format('YYYY-MM-DD HH:mm:ss')
        ]
    values.timezone = defaultValues.timezone
    values.repeatFreq = defaultValues.repeatFreq
    values.until = defaultValues.until
    values.applied_on_dates = defaultValues.applied_on_dates
    values.applied_on_days = defaultValues.applied_on_days
    values.applied_on_weeks = defaultValues.applied_on_weeks
    values.comment = defaultValues.comment
    values.replaces_other_entry = defaultValues.replaces_other_entry
    values.replaces_own_entry = defaultValues.replaces_own_entry
  }

  $externalResults.value = {}
  v$.value.$reset()
}

watch(values, () => {
  non_field_errors.value = []
})
watch(open, () => {
  if (open.value) {
    resetForm()
  }
})
watch(props, () => {
  if (props.mode === 'quick-add-sickness-absence') {
    // values.start_date = moment.utc().format('YYYY-MM-DD')
  }
})
watch([entryTypes, props], () => {
  if (props.mode === 'quick-add-sickness-absence' && entryTypes.value) {
    values.entry_type = entryTypes.value.find((entryType) => entryType.name === 'Sick Absence')
  }
})
</script>

<template>
  <BModal v-model="open" :no-close-on-backdrop="isPending" centered @hide="emit('hide')">
    <BForm>
      <BAlert
        :model-value="true"
        variant="danger"
        class="mb-[1rem]"
        v-for="error of non_field_errors"
        :key="error"
      >
        {{ error }}
      </BAlert>

      <div class="flex mb-[1rem]">
        <label class="col-form-label">
          <span class="icon icon-xs my-1 mx-3 fa fa-solid fa-user"></span>
        </label>
        <div class="flex-1">
          <SelectField
            :loading="isLoadingPeople"
            :options="people"
            label="name"
            v-model="values.person"
            required
            :clearable="false"
            :append-to-body="false"
            placeholder="Please select Team Member"
            class="mb-0"
          />
          <BFormInvalidFeedback :state="!v$.person.$error">
            <div v-for="error of v$.person.$errors" :key="error.$uid">{{ error.$message }}</div>
          </BFormInvalidFeedback>
        </div>
      </div>
      <div class="flex mb-[1rem]" v-if="mode !== 'quick-add-sickness-absence'">
        <label class="col-form-label">
          <span class="icon icon-xs my-1 mx-3 fa fa-solid fa-tasks-alt"></span>
        </label>
        <div class="flex-1">
          <SelectField
            :loading="isLoadingEntryTypes"
            :options="entryTypes"
            :selectable="
              (entryType: EntryType) =>
                values.repeatFreq === 'weekly' ? !entryType.is_specific_only : true
            "
            label="name"
            v-model="values.entry_type"
            :clearable="false"
            :append-to-body="false"
            placeholder="Please select Event Type"
            class="mb-0"
          />
          <BFormInvalidFeedback :state="!v$.entry_type.$error">
            <div v-for="error of v$.entry_type.$errors" :key="error.$uid">{{ error.$message }}</div>
          </BFormInvalidFeedback>
        </div>
      </div>
      <div class="flex mb-[1rem]">
        <label class="col-form-label">
          <span class="icon icon-xs my-1 mx-3 fa fa-solid fa-clock"></span>
        </label>
        <div class="flex-1">
          <div class="mb-[1rem]">
            <RangePickr
              v-model:range="values.range"
              v-model:timezone="values.timezone"
              :timezoneOptions="timezones"
              :is-loading-timezone-options="isLoadingTimezones"
              :max-diff="24"
              :all-day="values.entry_type?.requires_full_workday"
            />
            <BFormInvalidFeedback :state="!v$.range.$error">
              <div v-for="error of v$.range.$errors" :key="error.$uid">
                {{ error.$message }}
              </div>
            </BFormInvalidFeedback>
          </div>

          <div class="mb-[1rem] w-[180px]">
            <SelectField
              :options="repeatFreqOptions"
              :selectable="
                (option: RepeatFreqOption) =>
                  values.entry_type?.is_specific_only ? option.value !== 'weekly' : true
              "
              :reduce="(option: RepeatFreqOption) => option.value"
              v-model="values.repeatFreq"
              required
              :clearable="false"
              :append-to-body="false"
              :disabled="mode === 'edit'"
              class="mb-0"
            />
          </div>

          <div :class="{ hidden: values.repeatFreq === 'no-repeat' }">
            <BFormGroup label="End on:" class="mb-[1rem]">
              <div class="flex align-items-center gap-x-2">
                <FlatPickr
                  :config="{
                    minDate: values.range?.[0],
                    allowInput: true,
                    altInput: true,
                    altFormat: 'Y-m-d',
                    locale: { firstDayOfWeek: 1 }
                  }"
                  v-model="values.until"
                  placeholder="End Date"
                  :disabled="mode === 'edit'"
                />
              </div>
              <BFormInvalidFeedback :state="!v$.until.$error">
                <div v-for="error of v$.until.$errors" :key="error.$uid">
                  {{ error.$message }}
                </div>
              </BFormInvalidFeedback>
            </BFormGroup>

            <BFormGroup label="Repeat on:" :state="v$.applied_on_dates.$error">
              <template v-if="values.repeatFreq === 'daily'">
                <div class="mb-[1rem]">
                  <ApplyDatesSelect
                    v-model="values.applied_on_dates"
                    :start_date="values.range?.[0]"
                    :end_date="values.until"
                    :disabled="mode === 'edit' || !values.range?.[0] || !values.until"
                    placeholder="Please select Applicable Dates"
                  />
                  <BFormInvalidFeedback :state="!v$.applied_on_dates.$error">
                    <div v-for="error of v$.applied_on_dates.$errors" :key="error.$uid">
                      {{ error.$message }}
                    </div>
                  </BFormInvalidFeedback>
                </div>
              </template>
              <template v-else>
                <div class="mb-[1rem]">
                  <ApplyDaysSelect
                    v-model="values.applied_on_days"
                    :disabled="mode === 'edit' || !values.range?.[0] || !values.until"
                  />
                  <BFormInvalidFeedback :state="!v$.applied_on_days.$error">
                    <div v-for="error of v$.applied_on_days.$errors" :key="error.$uid">
                      {{ error.$message }}
                    </div>
                  </BFormInvalidFeedback>
                </div>
                <div class="mb-[1rem]">
                  <ApplyWeeksSelect
                    v-model="values.applied_on_weeks"
                    :start_date="values.range?.[0]"
                    :end_date="values.until"
                    :disabled="mode === 'edit' || !values.range?.[0] || !values.until"
                    placeholder="Please select Applicable Weeks"
                  />
                  <BFormInvalidFeedback :state="!v$.applied_on_weeks.$error">
                    <div v-for="error of v$.applied_on_weeks.$errors" :key="error.$uid">
                      {{ error.$message }}
                    </div>
                  </BFormInvalidFeedback>
                </div>
              </template>
            </BFormGroup>
          </div>
        </div>
      </div>
      <div class="flex mb-[1rem]">
        <label class="col-form-label">
          <span class="icon icon-xs my-1 mx-3 fa fa-solid fa-sticky-note"></span>
        </label>
        <div class="flex-1">
          <BFormTextarea v-model="values.comment" rows="3" max-rows="6" placeholder="Comment" />
          <BFormInvalidFeedback :state="!v$.comment.$error">
            <div v-for="error of v$.comment.$errors" :key="error.$uid">
              {{ error.$message }}
            </div>
          </BFormInvalidFeedback>
        </div>
      </div>
    </BForm>

    <template v-slot:ok>
      <BButton type="submit" :disabled="isPending" variant="primary" @click="onSubmit">
        {{ mode === 'edit' ? 'Update' : 'Submit' }}
      </BButton>
    </template>
    <template v-slot:cancel>
      <BButton type="button" variant="danger" @click="onDelete" v-if="mode === 'edit'">
        Delete
      </BButton>
      <BButton type="button" @click="onCancel" v-else>Cancel</BButton>
    </template>
  </BModal>

  <ConfirmModal
    v-model:open="isConfirmModalOpen"
    :is-delete="isDelete"
    :is-blanket-entry="isBlanketEntry"
    @confirm="onConfirm"
  />
</template>

<style scoped lang="scss"></style>
