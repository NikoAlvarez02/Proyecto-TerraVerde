document.addEventListener('DOMContentLoaded', () => {

    // Simulación de una base de datos de turnos
    let turnos = [
        { id: 1, paciente: 'Ana García', profesional: 'Juan Pérez', fecha: '2025-10-15', hora: '10:00', descripcion: 'Consulta inicial' },
        { id: 2, paciente: 'Carlos López', profesional: 'Sofía Rodríguez', fecha: '2025-10-16', hora: '11:30', descripcion: 'Sesión de seguimiento' },
        { id: 3, paciente: 'María Pérez', profesional: 'Juan Pérez', fecha: '2025-10-17', hora: '15:00', descripcion: 'Terapia conductual' },
    ];
    
    // Simulación de horarios ocupados para validación
    const horariosOcupados = [
        { profesional: 'Juan Pérez', fecha: '2025-10-17', hora: '10:00' },
        { profesional: 'Sofía Rodríguez', fecha: '2025-10-16', hora: '14:00' }
    ];

    const listadoTurnosDiv = document.getElementById('listado-turnos');
    const editFormContainer = document.getElementById('edit-form-container');
    const turnosTableBody = document.querySelector('#turnos-table tbody');
    const editTurnoForm = document.getElementById('edit-turno-form');
    const formTitle = document.getElementById('form-title'); // Nuevo: título del formulario
    const btnAgregarTurno = document.getElementById('btn-agregar-turno'); // Nuevo: botón para agregar
    const cancelarEditBtn = document.querySelector('.btn-cancelar-edit');
    
    // Inputs del formulario, los usamos para ambas acciones (agregar y editar)
    const formTurnoIdInput = document.getElementById('edit-turno-id');
    const formPacienteInput = document.getElementById('edit-paciente');
    const formProfesionalInput = document.getElementById('edit-profesional');
    const formFechaInput = document.getElementById('edit-fecha');
    const formHoraInput = document.getElementById('edit-hora');
    const formDescripcionInput = document.getElementById('edit-descripcion');

    function renderTurnos() {
        turnosTableBody.innerHTML = '';
        turnos.forEach(turno => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${turno.paciente}</td>
                <td>${turno.profesional}</td>
                <td>${turno.fecha}</td>
                <td>${turno.hora}</td>
                <td>
                    <button class="btn btn-editar" data-id="${turno.id}">Editar</button>
                    <button class="btn btn-eliminar" data-id="${turno.id}">Eliminar</button>
                </td>
            `;
            turnosTableBody.appendChild(row);
        });
    }

    // Nueva función para limpiar el formulario y prepararlo para un nuevo turno
    function setupFormForAdd() {
        formTitle.textContent = 'Registrar Turno';
        formTurnoIdInput.value = ''; // Vaciamos el ID para indicar que es un nuevo turno
        formPacienteInput.value = '';
        formProfesionalInput.value = '';
        formFechaInput.value = '';
        formHoraInput.value = '';
        formDescripcionInput.value = '';
        formPacienteInput.disabled = false; // Habilitamos el campo de paciente para nuevos turnos
        
        listadoTurnosDiv.classList.add('hidden');
        editFormContainer.classList.remove('hidden');
    }

    // Nueva función para preparar el formulario para editar un turno existente
    function setupFormForEdit(turno) {
        formTitle.textContent = 'Modificar Turno';
        formTurnoIdInput.value = turno.id;
        formPacienteInput.value = turno.paciente;
        formProfesionalInput.value = turno.profesional;
        formFechaInput.value = turno.fecha;
        formHoraInput.value = turno.hora;
        formDescripcionInput.value = turno.descripcion;
        formPacienteInput.disabled = true; // Deshabilitamos el campo de paciente para que no se pueda cambiar
        
        listadoTurnosDiv.classList.add('hidden');
        editFormContainer.classList.remove('hidden');
    }

    // Evento para el botón de "Agregar Turno"
    btnAgregarTurno.addEventListener('click', setupFormForAdd);

    // Eventos para los botones dentro de la tabla (Editar y Eliminar)
    turnosTableBody.addEventListener('click', (e) => {
        if (e.target.classList.contains('btn-editar')) {
            const turnoId = parseInt(e.target.dataset.id);
            const turnoAEditar = turnos.find(t => t.id === turnoId);
            if (turnoAEditar) {
                setupFormForEdit(turnoAEditar);
            }
        }

        if (e.target.classList.contains('btn-eliminar')) {
            const turnoId = parseInt(e.target.dataset.id);
            const confirmarEliminacion = confirm('¿Está seguro de que desea eliminar este turno?');
            if (confirmarEliminacion) {
                const turnoIndex = turnos.findIndex(t => t.id === turnoId);
                if (turnoIndex > -1) {
                    turnos.splice(turnoIndex, 1);
                    alert('Turno eliminado con éxito.');
                    renderTurnos();
                }
            } else {
                alert('La eliminación ha sido cancelada.');
            }
        }
    });

    // Evento para el envío del formulario (aquí se unifican las acciones)
    editTurnoForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const id = formTurnoIdInput.value;
        const nuevoPaciente = formPacienteInput.value.trim();
        const nuevoProfesional = formProfesionalInput.value.trim();
        const nuevaFecha = formFechaInput.value.trim();
        const nuevaHora = formHoraInput.value.trim();
        const nuevaDescripcion = formDescripcionInput.value.trim();

        if (!nuevoProfesional || !nuevaFecha || !nuevaHora || !nuevaDescripcion || (id === '' && !nuevoPaciente)) {
            alert('Complete todos los campos obligatorios.');
            return;
        }

        const esHorarioOcupado = horariosOcupados.some(horario => 
            horario.profesional === nuevoProfesional &&
            horario.fecha === nuevaFecha &&
            horario.hora === nuevaHora
        );

        if (esHorarioOcupado) {
            alert('El profesional no está disponible en el nuevo horario seleccionado.');
            return;
        }

        // Lógica unificada para agregar o modificar
        if (id === '') { // Es un nuevo turno (el ID está vacío)
            const nuevoId = turnos.length > 0 ? Math.max(...turnos.map(t => t.id)) + 1 : 1;
            const nuevoTurno = {
                id: nuevoId,
                paciente: nuevoPaciente,
                profesional: nuevoProfesional,
                fecha: nuevaFecha,
                hora: nuevaHora,
                descripcion: nuevaDescripcion
            };
            turnos.push(nuevoTurno);
            alert('Turno registrado con éxito.');

        } else { // Es un turno existente (el ID tiene un valor)
            const confirmarCambios = confirm('¿Desea confirmar estos cambios?');
            if (confirmarCambios) {
                const turnoIndex = turnos.findIndex(t => t.id === parseInt(id));
                if (turnoIndex > -1) {
                    turnos[turnoIndex].profesional = nuevoProfesional;
                    turnos[turnoIndex].fecha = nuevaFecha;
                    turnos[turnoIndex].hora = nuevaHora;
                    turnos[turnoIndex].descripcion = nuevaDescripcion;
                    alert('Turno modificado con éxito.');
                }
            } else {
                return; // Cancelar el submit si el usuario cancela la confirmación
            }
        }
        
        editFormContainer.classList.add('hidden');
        listadoTurnosDiv.classList.remove('hidden');
        renderTurnos();
    });

    // Evento para el botón de "Cancelar"
    cancelarEditBtn.addEventListener('click', () => {
        editFormContainer.classList.add('hidden');
        listadoTurnosDiv.classList.remove('hidden');
    });

    renderTurnos();
});