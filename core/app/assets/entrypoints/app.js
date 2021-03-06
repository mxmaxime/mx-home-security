import '../css/app.scss'

import {ThemeChoice} from "../js/elements/ThemeChoice"
import {Copyable} from "../js/elements/Copyable"
import {Form} from "../js/elements/Form"
import {dialogManager} from "../js/mount-vue-app"
import {ReloadBtn} from "../js/elements/ReloadBtn"

window.dialogManager = dialogManager

customElements.define('custom-form', Form, {extends: 'form'})
customElements.define('theme-choice', ThemeChoice)
customElements.define('copyable-value', Copyable)
customElements.define('reload-button', ReloadBtn)
