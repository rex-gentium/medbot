/*
Выполнить вручную после инициализации кластера:
sudo -u postgres psql
create user medbot with password '3285';
create database medbot with owner medbot;
*/

/* Справочник: Состояние конечного автомата */
create table state (
    id bigserial primary key,
    name text unique not null
);
insert into state (id, name) values
    (1, 'add_medication_enter_name'),
    (2, 'add_prescription_select_medication'),
    (3, 'add_prescription_enter_dose'),
    (4, 'add_prescription_enter_start_date'),
    (5, 'add_prescription_enter_end_date'),
    (6, 'add_prescription_select_event'),
    (7, 'add_prescription_enter_time'),
    (8, 'add_prescription_enter_conditions');

/* Пользователь */
create table "user" (
    id bigserial primary key,
    state_id bigint,
    session_data jsonb not null default '{}'::jsonb,
    constraint fk_user_state
        foreign key(state_id)
            references state(id)
            on delete set null
);
create index user_state_idx on "user"(state_id);

/* Препарат */
create table medication (
    id bigserial primary key,
    user_id bigint not null,
    name text not null,
    constraint fk_medication_user
        foreign key(user_id)
            references "user"(id)
            on delete cascade
);
create index medication_user_idx on medication(user_id);

/* Справочник: События */
create table event (
    id bigserial primary key,
    name text unique not null,
    rank int not null
);
insert into event (id, rank, name) values
    (1, 0, 'утром'),
    (2, 1, 'завтрак'),
    (3, 2, 'обед'),
    (4, 3, 'ужин'),
    (5, 4, 'на ночь');

/* Расписание приёма препарата на какой-либо период */
create table prescription (
    id bigserial primary key,
    user_id bigint not null,
    medication_id bigint not null,
    start_date date,
    end_date date,
    dose int not null default 1,
    event_id bigint,
    time_delta interval,
    constraint fk_prescription_user
        foreign key(user_id)
            references "user"(id)
            on delete cascade,
    constraint fk_prescription_medication
        foreign key(medication_id)
            references medication(id)
            on delete cascade,
    constraint fk_prescription_event
        foreign key(event_id)
            references event(id)
            on delete cascade
);
create index prescription_user_idx on prescription(user_id);
create index prescription_medication_idx on prescription(medication_id);
create index prescription_event_idx on prescription(event_id);
create index prescription_start_date_idx on prescription(start_date);
create index prescription_end_date_idx on prescription(end_date);

/* Справочник: Особое условие */
create table special_condition (
    id bigserial primary key,
    name text unique not null
);
insert into special_condition (id, name) values
    (1, 'по чётным дням'),
    (2, 'по нечётным дням');

/* Связка: Расписание приёма - Особое условие */
create table prescription_conditions (
    prescription_id bigint not null,
    condition_id bigint not null,
    primary key (prescription_id, condition_id),
    constraint fk_prescription_conditions_prescription
        foreign key(prescription_id)
            references prescription(id)
            on delete cascade,
    constraint fk_prescription_conditions_condition
        foreign key(condition_id)
            references special_condition(id)
            on delete cascade
);
create index prescription_conditions_prescription_idx on prescription_conditions(prescription_id);
create index prescription_conditions_condition_idx on prescription_conditions(condition_id);