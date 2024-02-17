Ext.ns('Ext.m3');

/**
 * @class Ext.ux.form.MultiSelectFilterColumn
 * @extends Ext.m3.MultiSelectField
 *
 * Колоночный фильтр для выбора множества значений.
 * Фильтр отправляет запрос на сервер при сворачивании комбобокса при условии,
 * что предыдущее состояние фильтра было изменено. В самом поле комбобокса
 * текстовое значение не отображается.
 */
Ext.m3.MultiSelectFilterColumn = Ext.extend(Ext.m3.MultiSelectField, {

    /**
     * Добавляет опцию Выделить все записи/Снять выделение всех записей
     */
    useOptAll: false,

    /**
     * Id опции Выделить все
     */
    optAllId: -5,

    optAllOnLabel: 'Снять выделение всех записей',
    divAllOn: '',

    optAllOffLabel: 'Выделить все записи',
    divAllOff: '',

    /**
     * Метод расширен для добавления функционала Выделить все записи/Снять выделение всех записей
     */
    initComponent:function() {
        Ext.m3.MultiSelectFilterColumn.superclass.initComponent.apply(this);

        this.useOptAll = this.initialConfig.useOptAll;

        if (this.useOptAll) {
            this.divAllOn = '<div>' + this.optAllOnLabel + '</div>';
            this.divAllOff = '<div>' + this.optAllOffLabel + '</div>';

            var defaultValue = Ext.decode(this.defaultValue),
                optionAllLabel,
                everythingSelected;

            everythingSelected = defaultValue.length === this.store.data.items.length;
            optionAllLabel = everythingSelected ? this.optAllOnLabel : this.optAllOffLabel;
            if (everythingSelected) {
                defaultValue.splice(0, 0, this.optAllId);
                defaultValue = Ext.encode(defaultValue);
                this.defaultValue = defaultValue;
                this.value = defaultValue;
            }

            var data = this.store.reader.readRecords([
                [this.optAllId, optionAllLabel]
            ]);
            this.store.insert(0, data.records);
        }
    },
    /**
     * Метод переопределен для добавления this.refreshItem(r)
     */
    initValue:function() {
        var i = 0, obj, values, val, record;

        if (this.store && this.value && this.mode === 'local') {
            //Случай, если контрол используется как локальный комбобокс
            //со множественным выбором
            values = Ext.util.JSON.decode(this.value);
            this.store.each(function (r) {
			    Ext.each(values, function (value) {
			        if (r.get(this.valueField) == value) {
			            this.checkedItems.push(r);
			            this.refreshItem(r);
			            return false;
			        }
			    }, this);
		    }, this);
        }
        else if (this.value) {
            //Попробуем создать значения из того что нам прислали с сервера
            //ожидаем что там будут некие объекты с полями значения и отображения
            values = Ext.util.JSON.decode(this.value);

            for (;i < values.length; i++) {
                val = values[i];

                if (typeof(val) !== 'object' ||
                    !( val[this.displayField] && val[this.valueField] )){
                    continue;
                }

                record = new Ext.data.Record();
                record.data[this.valueField] = val[this.valueField];
                record.data[this.displayField] = val[this.displayField];

                this.checkedItems.push(record);
            }
        }

        Ext.m3.MultiSelectField.superclass.initValue.call(this);
    },
    /**
     * Заполняет сохранённое значение фильтра
     * @param {string} value
     */
    fillPrevSavedValue: function(value) {
        var decoded = Ext.util.JSON.decode(value),
            storeDataCount = this.store.data.items.length,
            countWithoutAllOption = storeDataCount - 1,
            newValue = [];

        this.checkedItems.splice(0, this.checkedItems.length);
        if (this.useOptAll && decoded.length === countWithoutAllOption) {
            var recordAll = this.store.getById(this.optAllId);
            this.checkedItems.push(recordAll);
        }

        for (var i = 0; i < decoded.length; i++) {
            var id = decoded[i],
                record = this.store.getById(id);

            if (record) {
                this.checkedItems.push(record);
                newValue.push(record.id);
            }
        }

        return Ext.util.JSON.encode(newValue);
    },
    /**
     * Возвращает boolean, в зависимости от того выбрана ли опция Выделить все записи/Снять выделение всех записей
     */
    isOptAllChecked: function() {
        var allChecked = false;

        for (var i = 0; i < this.checkedItems.length; i++) {
            if (this.checkedItems[i].data[this.valueField] === this.optAllId) {
                allChecked = true;
                break;
            }
        }

        return allChecked;
    },
    /**
     * Метод расширен для добавления функционала Выделить все записи/Снять выделение всех записей
     */
    onTriggerDropDownClick: function () {
        Ext.m3.MultiSelectFilterColumn.superclass.onTriggerDropDownClick.call(this);

        if (this.useOptAll) {
            var allChecked = this.isOptAllChecked();
            this.view.all.elements[0].innerHTML = allChecked ? this.divAllOn : this.divAllOff;
        }
    },
    collapse : function(){
        if(!this.isExpanded()){
            return;
        }
        this.list.hide();
        Ext.getDoc().un('mousewheel', this.collapseIf, this);
        Ext.getDoc().un('mousedown', this.collapseIf, this);
        this.fireEvent('collapse', this);
        if (this.prevValue != this.value) {
            this.fireEvent("select", this, this.checkedItems);
        }
    },
    /**
     * Метод расширен для добавления функционала Выделить все записи/Снять выделение всех записей
     */
    getText : function () {
		var value = [];
		Ext3.each(this.checkedItems, function (record) {
			value.push(record.eqcode || record.get(this.displayField));
		}, this);
		if (value.length > 1 && this.multipleDisplayValue){
			return this.multipleDisplayValue;
		} else {
		    if (this.useOptAll) {
                value.remove(this.optAllOnLabel);
                value.remove(this.optAllOffLabel);
            }
			return value.join(this.delimeter + ' ');
		}
	},
    /**
     * Метод расширен для добавления функционала Выделить все записи/Снять выделение всех записей
     */
    onSelect : function (record, checkedIndex) {
        if (record.data.id === this.optAllId) {
            var allChecked = this.isOptAllChecked(),
                storeItems = this.store.data.items;

            for (var i = 0; i < storeItems.length; i++) {
                var item = storeItems[i],
                    index = this.findCheckedRecord(item);

                if (allChecked && index !== -1) {
                    this.checkedItems.remove(this.checkedItems[index]);
                } else if (index === -1) {
                    this.checkedItems.push(item);
                }
                this.refreshItem(item);
            }

            this.view.all.elements[0].innerHTML = allChecked ? this.divAllOff : this.divAllOn;

            this.setValue(this.getValue());
        } else {
            this.selectCommonRecord(record, checkedIndex);
        }
	},
    /**
     * Обрабатывает выбор обычной опции (все кроме Выделить все записи/Снять выделение всех записей)
     * @param record: Ext.data.Record
     * @param checkedIndex: integer
     */
    selectCommonRecord: function(record, checkedIndex) {
        var recordAll = this.store.getById(this.optAllId),
            index = this.findCheckedRecord(record);

        if (this.fireEvent("beforeselect", this, record, checkedIndex) !== false) {
            if (index === -1) {
                this.checkedItems.push(record);
                if (this.useOptAll && this.checkedItems.length === this.store.data.items.length - 1) {
                    this.checkedItems.push(recordAll);
                    this.view.all.elements[0].innerHTML = this.divAllOn;
                }
            } else {
                this.checkedItems.remove(this.checkedItems[index]);

                if (this.useOptAll) {
                    if (this.checkedItems.indexOf(recordAll) !== -1) {
                        this.checkedItems.remove(recordAll);
                        this.refreshItem(recordAll);
                    }

                    this.view.all.elements[0].innerHTML = this.divAllOff;
                }
            }

            this.refreshItem(record);
            this.setValue(this.getValue());
        }
    },
    /**
     * Метод расширен для добавления функционала Выделить все записи/Снять выделение всех записей
     */
    getValue : function () {
		var value = [];

		Ext3.each(this.checkedItems, function (record) {
			value.push(record.eqid || record.get(this.valueField));
		}, this);

		if (this.useOptAll) {
		    value.remove(this.optAllId);
        }
		return Ext3.util.JSON.encode(value);
	},
    setValue:function(v) {

        if (!v || v === '[]'){
            this.hideClearBtn();
        }
        else {
            this.showClearBtn();
        }
        this.prevValue = this.value;
        this.value = this.getValue();

        this.setRawValue(this.getText());
        if (this.hiddenField) {
            this.hiddenField.value = this.value;
        }
        if (this.el) {
            this.el.removeClass(this.emptyClass);
        }
    },
    triggerBlur: function () {
        if (this.focusClass) {
            this.el.removeClass(this.focusClass);
        }
        if (this.wrap) {
            this.wrap.removeClass(this.wrapFocusClass);
        }
        this.validate();
    }
});

Ext.reg('m3-multiselect-filter-column', Ext.m3.MultiSelectFilterColumn );
